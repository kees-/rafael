(ns scripts.project
  (:require [babashka.fs :as fs]
            [clojure.string :as s]))

;; ========== PROJECT ==========================================================
(defn hydrate
  [& _]
  (doseq [dir ["audio" "contents" "frames" "masks" "panes" "target"]]
    (fs/create-dirs dir)))

(defn- get-files
  [dir]
  (fs/glob dir "[0-9][0-9][0-9]-*" {:follow-links true}))

(defn- pair-dirs
  "Given two dirs of files with %03d- prefixes, return matching pairs."
  [a b]
  (let [prep #(map (juxt identity fs/file-name) (get-files %))
        [a-seq b-seq] (map prep [a b])
        f (fn [a-val]
            (let [prefix (last a-val)
                  matcher (re-pattern (format "^%s-.*" prefix))
                  uhh #(re-find matcher (second %))]
              (when-let [b-val (some #(when (uhh %) %) b-seq)]
                [(first a-val) (first b-val) prefix])))
        prefixes (map #(conj % (second (re-find #"^(\d+)-[^/]*" (second %)))) a-seq)]
    (remove nil? (map f prefixes))))

;; ========== FFMPEG ===========================================================
(defn ffcutout
  [argm]
  (let [{:keys [video mask out]} argm
        ffargs ["ffmpeg"
                "-v 16 -stats -y"
                (format "-i %s -i %s" video mask)
                "-filter_complex \""
                "[1:v] alphaextract [a];"
                "[0:v][a] alphamerge\""
                (format "-c:v qtrle -an -shortest %s" out)]]
    (s/join " \\\n  " ffargs)))

(defn- filter-overlays
  [panes]
  (loop [out ["[1:v] format=rgba [bg0];"]
         [cur & remaining] panes]
    (if-not cur
      out
      (let [c (count out)
            s (format "[bg%s][%s:v] overlay=format=auto, setsar=1, format=rgba [bg%s];"
                      (dec c) (inc c) c)]
        (recur (conj out s) remaining)))))

(defn- ffpress
  [{:keys [frame base panes-dir video-dir masks-dir out]}]
  (let [main-inputs (format "-i %s -i %s" frame base)
        panes (sort (map last (pair-dirs video-dir masks-dir)))
        pane-inputs (map #(format "-i %s/%s.mov" panes-dir %) panes)
        ffargs (flatten ["ffmpeg"
                         "-v 16 -stats -y"
                         main-inputs
                         pane-inputs
                         "-filter_complex \""
                         (filter-overlays panes)
                         (format "[bg%s][0:v] blend=all_mode=darken:all_opacity=1, format=rgba\"" (count panes))
                         (format "-c:v qtrle -an -shortest %s" out)])]
    (s/join " \\\n  " ffargs)))

(defn- mass-cutout
  [{:keys [video-dir masks-dir]}]
  (let [prep (fn [[video mask prefix]]
               {:video video
                :mask mask
                :out (format "panes/%s.mov" prefix)})
        inputs (->> (pair-dirs video-dir masks-dir)
                    sort
                    (map prep))]
    
    (mapv ffcutout inputs)))

(defn press-to-file
  [{:keys [video-dir masks-dir panes-dir frame base pressfile outfile]}]
  (let [cutouts (mass-cutout {:video-dir video-dir
                              :masks-dir masks-dir})
        presser (ffpress {:panes-dir panes-dir
                          :video-dir video-dir
                          :masks-dir masks-dir
                          :frame frame
                          :base base
                          :out outfile})]
    (spit pressfile (s/join "\n\n" (conj cutouts presser))))
  (fs/set-posix-file-permissions (fs/file pressfile) "rwxrwx---")
  (println "Written."))

(comment
  (press-to-file {:video-dir "contents"
                  :masks-dir "masks"
                  :panes-dir "panes"
                  :pressfile "press"
                  :frame "frames/frame.png"
                  :base "frames/sky.png"
                  :outfile "target/styling-acteon.mov"}))
