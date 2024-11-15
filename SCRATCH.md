```sh
ffmpeg -ss 6:06 -t 20 -i  "/Users/kees/Downloads/Everything Visible is Empty (1975).mp4"  \
  -vf scale=1080:1250,setsar=1 \
  -an -b:v 10k -c:v libx264 -y palette.mp4

ffmpeg -v 16 -stats -y -i palette.mp4 -i target/combined.png \
  -filter_complex "[1:v] alphaextract [a]; [0:v][a] alphamerge" \
  -c:v qtrle -an -shortest combined.mov

ffmpeg -v 16 -stats -y -i church.bmp -i church.bmp -i combined.mov \
  -filter_complex "[1:v] format=rgba [bg0]; [bg0][2:v] overlay=format=auto, setsar=1, format=rgba [bg1]; [bg1][0:v] blend=all_mode=darken:all_opacity=1, format=rgba" \
  -c:v qtrle -an -shortest frap.mov
```
