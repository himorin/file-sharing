# データベース設計

## テーブルリスト・データ

* `tenants`: テナントリスト
  * `tid`: テナントID
  * `adminkey`: 管理キー
  * `name`: テナント名
  * `memo`: テナントの説明
  * `redirect`: ファイルダウンロードのリダイレクト先
* `files`: ファイルリスト
  * `tid`: テナントID
  * `fid`: ファイルID
  * `name`: ファイル名
  * `mimetype`: MIME type (拡張子を入れる)
* `labels`: ラベルリスト
  + `tid`: テナントID
  * `lid`: ラベルID
  * `isgroup`: グループ扱いをするかどうか
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
  redirect          text                NULL                             
) DEFAULT CHARSET=utf8

CREATE TABLE files (
  tid               text            NOT NULL                             ,
  fid               text            NOT NULL UNIQUE                      ,
  name              text            NOT NULL                             ,
  mimetype          text            NOT NULL                             
) DEFAULT CHARSET=utf8

CREATE TABLE labels (
  tid               text            NOT NULL                             ,
  lid               text            NOT NULL UNIQUE                      ,
  isgroup           tinyint         NOT NULL DEFAULT 0                   ,
  name              text            NOT NULL                             ,
  memo              text                NULL                             
) DEFAULT CHARSET=utf8

CREATE TABLE flabel (
  fid               text            NOT NULL                             ,
  lid               text            NOT NULL                             
) DEFAULT CHARSET=utf8

CREATE TABLE glabel (
  gid               text            NOT NULL                             ,
  lid               text            NOT NULL                             
) DEFAULT CHARSET=utf8
```
