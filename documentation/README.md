# Documentation Workspace

This folder will contain the CBSE IP project documentation, diagrams, tables, and report content.

## MySQL Workbench Connection

If you want to create a new connection for the project package in MySQL Workbench, use the same settings the app expects by default:

- Connection name: `PMLA-SCWE Project Package`
- Hostname: `127.0.0.1` or `localhost` only. Do not include `:3306` in this field.
- Port: `3306`
- Username: `root`
- Password: your local MySQL root password
- Default schema/database: `pmla_scwe`

### Quick steps

1. Open MySQL Workbench.
2. Click the plus icon next to MySQL Connections.
3. Enter the connection name above.
4. Set Hostname, Port, Username, and Password.
5. Click Test Connection.
6. If the test succeeds, save the connection and open it.

### After connecting

Run `schema.sql` to create the database and tables if they do not exist yet. The schema file creates `pmla_scwe` and uses it automatically.

### If Workbench says `Unknown database 'pmla_scwe'`

That means the connection is fine, but the schema has not been created yet. In that case:

1. Leave the Default Schema field empty for the first connection test.
2. Connect to MySQL using `root`, host `127.0.0.1`, and port `3306`.
3. Open `schema.sql` in Workbench or run it in the SQL editor.
4. Execute the script so `pmla_scwe` is created.
5. Reopen or edit the connection and set Default Schema to `pmla_scwe`.

If you prefer, you can also create the database manually first with:

```sql
CREATE DATABASE pmla_scwe;
```
