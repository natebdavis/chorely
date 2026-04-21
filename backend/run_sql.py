from supabase import create_client

url = "https://hxnfdduifuqqjxwzgyhj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh4bmZkZHVpZnVxcWp4d3pneWhqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTExODk0OSwiZXhwIjoyMDg2Njk0OTQ5fQ.V-mcJ4f78tqskrk5yFnPJhmzcIzyBLmuWx6lclQZjn4"

supabase = create_client(url, key)


res = supabase.table("chore_templates").select("*").limit(1).execute()
print(res)