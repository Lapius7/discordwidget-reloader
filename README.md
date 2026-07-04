# Discord Widget Reloader

Discordの実験的機能「Profile Widgets v2」で、プロフィールに表示したウィジェットが
`Your game stats are still syncing. Keep playing!`（同期中のまま）から進まなくなる問題を、
一定間隔でDiscordの内部APIにステータスをPATCHし続けることで回避する常駐コンテナです。

参考: [Discord Widgets — chloecinders.com](https://chloecinders.com/blog/discord-widgets)

## ⚠️ 免責事項

- Profile Widgets v2は**Discordが正式公開していない実験的機能**です。予告なく仕様変更・廃止される可能性があります。
- Bot Tokenを使った内部APIへの直接アクセスは、Discordの利用規約上グレーゾーンです。**自己責任で利用してください。**
- 大量アカウントでの利用や過度に短い同期間隔での連打など、Discordのインフラに負荷をかける使い方はしないでください。
- 本リポジトリの作者は、利用によって生じたアカウント停止等のいかなる不利益についても責任を負いません。

## 前提条件（このコンテナの範囲外・事前にDiscord上で完了させておくこと）

1. [Discord Developer Portal](https://discord.com/developers/applications) でアプリケーションを作成し、`Games` → `Social SDK` を有効化する
2. アプリケーションをチーム所有にする（個人所有のままだと `Games` タブの条件を満たせない場合がある）
3. ブラウザの開発者コンソールで実験フラグを有効化し、`Widget` タブを表示させて、Widgetを作成・Publishする
   - フラグ名は変更される可能性があるため、最新情報は上記ブログ記事や関連コミュニティを参照してください
4. OAuth2で `openid` + `sdk.social_layer` スコープを許可し、ユーザートークンでの認可を済ませる
5. Discordクライアントのコンソールで、対象アプリケーションIDを featured アプリケーション一覧に追加する
6. ユーザー設定 → プロフィール編集 → Profile Widgets から、作成したウィジェットをプロフィールに追加する

上記が完了していないと、このコンテナがPATCHを送ってもプロフィール上の表示は変わりません。

## ディレクトリ構成

```
discordwidget-reloader/
├── docker-compose.yml
├── Dockerfile
├── .env.example              ← コピーして .env を作成
├── widget_data.sample.json   ← コピーして widget_data.json を作成
└── app/
    └── sync.py                ← 定期PATCH送信スクリプト
```

## セットアップ

```bash
# 1. リポジトリを取得
git clone <このリポジトリのURL>
cd discordwidget-reloader

# 2. 環境変数ファイルを作成
cp .env.example .env
nano .env
# DISCORD_APPLICATION_ID, DISCORD_USER_ID, DISCORD_BOT_TOKEN を設定

# 3. 送信するウィジェットデータを作成
cp widget_data.sample.json widget_data.json
nano widget_data.json
# Developer Portal の Games → Widget → Sample Data タブの
# 「Generate JSON」で生成したJSONを参考に、自分のウィジェット構成に合わせて書き換える

# 4. 起動
docker compose up -d --build

# 5. ログ確認（一定間隔でPATCHの成否が出力される）
docker compose logs -f

# 6. 停止
docker compose down
```

## 設定項目

| 環境変数 | 説明 |
|---|---|
| `DISCORD_APPLICATION_ID` | Developer PortalのGeneral Informationに表示されるApplication ID |
| `DISCORD_USER_ID` | ウィジェットを表示する自分のDiscordユーザーID |
| `DISCORD_BOT_TOKEN` | Botページで Reset Token して取得したトークン |
| `SYNC_INTERVAL_SECONDS` | PATCH送信間隔（秒）。デフォルト300 |

## VPSなど常時稼働環境で動かす場合

このコンテナが動いている間だけ同期が維持されます。コンテナを止めると、最後に送信した内容が
そのまま表示され続けますが、一定時間（数分〜数十分程度）経過すると再び「同期中」表示に戻ります。

自宅PCなど電源を落とす環境で運用している場合、PCがオフの間は同期が途切れるため、
常時起動しているVPSやNAS等でこのコンテナを動かすことをおすすめします。

## トラブルシューティング

- **`403 {"message": "internal network error", "code": 40333}` が出る場合**
  `Authorization: Bot <token>` のリクエストに、ブラウザを偽装した `User-Agent` ヘッダーを
  付けているとCloudflare側で不審なリクエストとして弾かれることがあります。
  `sync.py` では `User-Agent` を明示的に設定していません（Pythonのデフォルトのまま送信）。
  独自にヘッダーを追加する場合は注意してください。
- **PATCHは成功しているのにプロフィール表示が変わらない場合**
  Discordクライアント側のキャッシュが残っていることがあります。`Ctrl+Shift+R`（ブラウザ）や
  Discordアプリの再読み込み（`Ctrl+R`）を試してください。Widget構成自体を編集・Publishした
  直後も同様です。

## ライセンス

[MIT](LICENSE)
