import ffmpeg
 
path = "E:/Cubase プロジェクト/同期音源/2023 SANOWA ずっと真夜中でいいのに。/Vocal_Audio/"
# 入力
stream = ffmpeg.input(path+"お勉強 1.m4a")
 
# 出力
stream = ffmpeg.output(stream, path+"output.mp3")
 
# 実行
ffmpeg.run(stream)