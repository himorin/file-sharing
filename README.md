# ファイル共有用のウェブアプリ

## 要件リスト

* マルチテナント型として、共有のすべての操作は各テナント内で完結する形にする
  * 各テナントごとに管理画面が提供される
* 各テナント内に特定条件付きのアップロードフォームの設定が可能になるようにする
  * アップロードしたファイルのダウンロード用リンクを提供するかどうかは選択可能にする
* ファイルに付随する情報の設定
  * ファイルについての説明（自由文章）
  * ラベル機能
* 個別ファイルはハッシュキーで特定されるようにして、ダウンロードリンクが自動的にできるようにする
  * (TBD) ダウンロード用画面をいったん挟むか？ (ファイルについての説明とかを表示する画面は必要に思える)
* 複数ファイル一括アップロード機能・グループ化情報の保持
  * アップロード画面は複数ファイルをアップロードできるようにする
  * グループのダウンロード画面は、グループのファイル全部をzipで落とすか、個別ファイルを落とすかの両方を表示する
* 一括ダウンロード機能
  * テナント内全部
  * テナント内の特定のラベルが付いたもの全部
    * 複数ラベルが存在するのを条件とするのもできるようにするか？
* アクセスキーでの制限
  * 管理画面は必須
  * アップロード・ダウンロードの画面はhash URLにしてアクセスキーをなくす？
    * hash URLの上にアクセスキーを付けてどの程度の効果が見込まれるか？ (リンク漏れ対策には有効ではある)
* 特定のドメインをターゲットにproxy的な扱いをする機能を入れる
  * proxyで取ってくるファイルの追加は管理画面からのみ設定できるようにする
  * fes-storageとかの大容量ビデオ置き場系とかから (BASICはauth設定で内部扱いにしておく必要あり)
  * アーカイブ化として、テナント全体をproxyのターゲットに置き換える機能も提供する
    * 裏側のストレージはテナントごとのハッシュディレクトリの必要がある
    * proxyのターゲットからの提供にした際に一括ダウンロードをどうやって実現するか (proxy先にPOSTでのzip化するだけのスクリプトを置く？)
* 単一テナント全体のアーカイブ機能
  * 一括で転送先URLのヘッダを指定できるようにする
  * ダウンロードAPIはproxyとし、MIME typeはデータベースからとってつける (転送先は単なるストレージ扱い)
  * 対象ファイルリストを出力できる機能を付けるが、ハッシュディレクトリでのzip化や一括消去は付けない (シェルでやれ、で)

### 要件整理

* アップロード・ダウンロードのリンクの提供
  * ダウンロードページはすべてテナント情報が入らないリンクとする
  * アップロードページは、テナント管理画面からのアップロード、もしくは、グループに紐づける(テナント情報は入らない)アップロード画面のみとする
    * グループに紐づかない外部からのアップロードは受け付けない (このカテゴリでファイル欲しいからここに上げて、という際はなんらかの紐づいたグループがあるはず)
    * テナント管理画面からのアップロードの時のみ、ラベル付与などすべての機能が編集可能にする (内部関係者による利用)
* グループとラベルの関係
  * 各ファイルは一つのグループにしか所属できない
  * ラベルはファイルやグループに対して複数付けられる
  * 同じテナント内ではグループ・ラベル問わず同じ名前の物は複数存在できない
  * グループにのみ専用のアップロード画面が提供される
  * グループ・ラベル問わず、ハッシュを利用した一括ダウンロード画面が提供される
* グループについて
  * 内部的にはラベルの特殊形態とする
  * テナント管理画面内のアップロードでは2つのアップロード方法を選択できるようにする: 複数ファイルアップロード、zipファイルアップロード
    * 複数ファイルを同時にアップロード可能とする、この場合既定でグループ化を行う。(グループ解除は不可)
    * zipファイルアップロードではサーバ側で展開し、グループ化を行う
  * グループに紐づいたアップロード画面ではアップロードされたファイルは自動的にグループに紐づく、ただし複数ファイル同時アップロードでもサブグループなどは発生しない
  * グループはラベルなどの一括ダウンロードの場合にはディレクトリに読み替える
  * グループにラベルが付いた場合、その中の個別ファイルから該当のラベルを外すことは不可、個別ファイルへのラベルの追加は許可する
* ファイルに付属した情報の編集について
  * テナント管理画面もしくはアップロードを行った画面でのみ、ファイルの説明・ファイル名の編集を可能にする
  * ファイルへのラベルの追加・削除はテナント管理画面からのみ行える
* ダウンロード画面の構成
  * 個別ファイルダウンロードでは紐づいたテナント情報(テナント管理画面へのリンクなし)やラベルなどを含めたファイル情報を表示し、ダウンロードリンクを出す
  * グループ・ラベルの画面では上記に加えて、まとめてのダウンロードリンクも提供する

## システム・URL構成

* 基本要件
  * 画面についてはserver pathでの扱いとし、htmlのスクリプトでpathを見てアクセス情報とする
* `/` : トップページはシステム概要とリンク（利用説明・管理画面）を掲載程度
* `/tn/<tenant>/` : テナントについての説明とリンク（管理画面; 管理用キー必須）
  * `/tn/<tenant>/admin/` : ラベル・グループなどの管理画面 (管理用キー必須とする)
  * `/tn/<tenant>/uploads/` : アップロードデータの一覧、編集画面
* `/up/<hash>/` : グループへのファイル追加画面
* `/dl/<hash>/` : 単一ファイルの表示画面
* `/dg/<hash>/` : グループ・ラベルの表示画面
* `/docs/` : システムマニュアル
* `/admin/` : 全体管理用画面 (BASICも付けてもいいかも？＆ほぼテナントリストだけ)
  * `/admin/api/` : 全体管理系専用API用ディレクトリ
  * `/admin/api/tenants.cgi` : テナント一覧、新規テナント追加機能
* `/api/` : API用ディレクトリ
  * `/api/dl.cgi?` : ダウンロードAPI
    * `/api/dl.cgi?fid=<hash>` : 個別ファイルダウンロード (単一ファイルを提供)
    * `/api/dl.cgi?lid=<hash>` : ラベル・グループの一括ダウンロード (まとめてzipで提供)
  * `/api/info.cgi?` : アセット情報API
    * `/api/info.cgi?fid=<hash>` : ファイル情報のjsonデータ
    * `/api/info.cgi?lid=<hash>` : ラベル・グループ情報のjsonデータ
  * `/api/up.cgi`: ファイルアップロードAPI、jsonデータとファイルデータをmultipartで2つ
  * `/api/tn.cgi?tn=<tenant>`: テナントに関する情報


## API機能要件

* 前提
  * テナントのリストは全体管理画面(admin)でのみ供給する
