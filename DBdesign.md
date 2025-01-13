# データベース設計

## テーブルリスト・データ

* `tenants`: テナントリスト
  * `tid`: テナントID
  * `adminkey`: 管理キー
  * `name`: テナント名
  * `memo`: テナントの説明
  * `redirect`: ファイルダウンロードのリダイレクト先
  * `noup`: フラグ (アップロード停止)
* `files`: ファイルリスト
  * `tid`: テナントID
  * `gid`: グループID (lidの方)
  * `fid`: ファイルID
  * `name`: ファイル名
  * `mimetype`: MIME type (拡張子を入れる)
  * `memo`: ファイルの説明
  * `dt`: アップロード日時
  * `size`: ファイルサイズ (byte)
  * `flags`: フラグ (利用していない)
* `labels`: ラベルリスト
  * `tid`: テナントID
  * `lid`: ラベルID
  * `gid`: グループのアップロード用ID (NULLの場合はラベル)
  * `name`: ラベル名
  * `memo`: ラベルの説明
* `flabel`: ファイルへのラベルのリスト
  * `fid`: ファイルID
  * `lid`: ラベルID
* `glabel`: グループへのラベルのリスト
  * `gid`: グループID (lid相当)
  * `lid`: ラベルID

## SQL

```
CREATE DATABASE file_sharing;
GRANT delete,insert,lock tables,select,update,drop,create,index,references,CREATE TEMPORARY TABLES, alter on file_sharing.* to file_sharing@localhost identified by 'XXX';
```

```
CREATE TABLE tenants (
  tid               text            NOT NULL UNIQUE                      ,
  adminkey          int UNSIGNED    NOT NULL                             ,
  name              text            NOT NULL                             ,
  memo              text            NOT NULL                             ,
  redirect          text                NULL                             ,
  noup              tinyint         NOT NULL DEFAULT 0                   
) DEFAULT CHARSET=utf8;

CREATE TABLE files (
  tid               text            NOT NULL                             ,
  gid               text            NOT NULL                             ,
  fid               text            NOT NULL UNIQUE                      ,
  name              text            NOT NULL                             ,
  mimetype          text            NOT NULL                             ,
  memo              text            NOT NULL                             ,
  dt                DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP   ,
  size              int             NOT NULL DEFAULT 0                   ,
  flags             tinyint         NOT NULL DEFAULT 0                   
) DEFAULT CHARSET=utf8;

CREATE TABLE labels (
  tid               text            NOT NULL                             ,
  lid               text            NOT NULL UNIQUE                      ,
  gid               text                NULL                             ,
  name              text            NOT NULL                             ,
  memo              text                NULL                             
) DEFAULT CHARSET=utf8;

CREATE TABLE flabel (
  fid               text            NOT NULL                             ,
  lid               text            NOT NULL                             
) DEFAULT CHARSET=utf8;

CREATE TABLE glabel (
  gid               text            NOT NULL                             ,
  lid               text            NOT NULL                             
) DEFAULT CHARSET=utf8;
```
