heroku login

heroku config:get DATABASE_URL -a wpp-pricetracker
heroku pg:pull DATABASE_URL local_dbname --app wpp-pricetracker
heroku pg:psql
psql DATABASE_URL=postgres://u3tkr17grvffps:pa68dc90528eb9e021782dcc6239c2cfdbbc4bb7f5a494a851a521adbc124cb38@cd5gks8n4kb20g.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d6m61lm90g1mg2

\dt
Select * FROM products

# psql -h localhost -U your_username -d your_database_name
psql -h localhost -U postgres -d price_tracker

pg_dump postgres://username:password@hostname:port/dbname > heroku_backup.sql

# psql -h localhost -U your_local_username -d price_tracker -f heroku_backup.sql

