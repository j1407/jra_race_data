https://gist.github.com/datasciesotist/8d7d792182e1fece6e48

プログラムに関して、上記のコードを一部書き換えています。
とりあえず今の所(2019/01/22現在)はエラーは発生せずに稼働します。
実行には、最初の数行目の所にある、yea=(年)とmon=(月)を変更して実行してください。
プログラムを書き換えることで、1年分くらいならまとめて実行することはすぐできると思います。

2018年のJRA全レースの結果です。
中止、除外、競争中止、失格についてのデータはありません。
一部競馬場の障害レースのコース(右回り)のデータに特殊文字が入っているので、そこは整形してください。
このデータはご自由にお使いください。

・JRA_Race_Get.py
install する必要があるもの
python3系,request,bs4,pandas,lxml くらいだと思います。
