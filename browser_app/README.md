# Multiverse Browser

PythonとQt WebEngineで作られた、量子ツインエンジン内蔵デスクトップWebブラウザです。

## セットアップ

```bash
cd browser_app
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 起動

```bash
.venv/bin/python browser.py
```

タブ、戻る・進む、再読み込み、アドレス検索、ポップアップのタブ表示、
ファイルダウンロードに対応しています。ツールバーの `⚛²` ボタンを押すと、
2つの量子回路を並列実行・比較するQuantum Twin Engineが新しいタブで開きます。
