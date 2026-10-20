# 主要な一次資料と確認先

- [MDN HTML](https://developer.mozilla.org/ja/docs/Web/HTML)
- [MDN JavaScript](https://developer.mozilla.org/ja/docs/Web/JavaScript)
- [MDN HTTP](https://developer.mozilla.org/ja/docs/Web/HTTP)
- [PHP公式マニュアル（日本語）](https://www.php.net/manual/ja/)
- [PHP PDO::prepare](https://www.php.net/manual/ja/pdo.prepare.php)
- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP IDOR Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)
- [OWASP Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [MySQL Reference Manual](https://dev.mysql.com/doc/refman/8.4/en/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

**学習時の注意：** 資料の参照先は更新されることがあります。コード断片のPHPやDBの方言・対応バージョンを確認してください。

## Cookie・セッション乗っ取り編（2026-10-20に参照先確認）

- [NIST SP 800-63B-4 — Session Management](https://pages.nist.gov/800-63-4/sp800-63b/session/)：セッション秘密、HTTPS、Cookie属性、期限、再認証
- [MDN — Set-Cookie](https://developer.mozilla.org/ja/docs/Web/HTTP/Reference/Headers/Set-Cookie)：属性・接頭辞・Partitionedの意味
- [OWASP — Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)：IDの発行・再生成・ログアウト・監査
- [OWASP — Cookie Theft Mitigation](https://cheatsheetseries.owasp.org/cheatsheets/Cookie_Theft_Mitigation_Cheat_Sheet.html)：異常検知と誤判定
- [OWASP — XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)：HTML/JSの注入境界
- [OWASP — CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)：自動Cookie送信の危険
- [PHP公式 — セッション管理の基礎](https://www.php.net/manual/ja/features.session.security.management.php)：strict mode、再生成と競合対策
- [Google Security — DBSC（2026-04-09）](https://blog.google/security/protecting-cookies-with-device-bound-session-credentials/)：製品での展開発表
- [W3C — DBSC Working Draft](https://www.w3.org/TR/dbsc-1/)：標準仕様の進捗（Working Draft）
- [Microsoft Entra — Token Protection](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-token-protection)：プラットフォーム固有のデバイス結合
