from fastapi import FastAPI, Request
from api import router
import os
import uvicorn
import psycopg2

app = FastAPI()

# Database connection details (same as your Railway environment)
DB_CONFIG = {
    "dbname": "railway",
    "user": "postgres",
    "password": "teotNFnQltbMaVzzqzarDvlptWuAmbSx",
    "host": "shortline.proxy.rlwy.net",
    "port": "18922"
}

def create_news_table():
    """ Create the 'news' table inside Railway PostgreSQL """
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS news (
        id SERIAL PRIMARY KEY,
        instrument TEXT NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        published_at TIMESTAMP NOT NULL
    );
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(CREATE_TABLE_SQL)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Table 'news' created successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")

# Run table creation when the bot starts
create_news_table()

# Include the sentiment API routes
app.include_router(router)

@app.get("/")
async def home(request: Request):
    print(f"✅ Received request from: {request.client}")
    return {"message": "Sentiment Data Centre API is running!"}

@app.get("/news")
def get_news():
    """ Fetch news data from PostgreSQL and return as JSON """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT instrument, title, url, published_at FROM news ORDER BY published_at DESC LIMIT 100;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Convert to JSON format
        news_list = []
        for row in rows:
            news_list.append({
                "instrument": row[0],
                "title": row[1],
                "url": row[2],
                "published_at": row[3]
            })
        
        return {"news": news_list}

    except Exception as e:
        return {"error": str(e)}

# Log FastAPI startup message
port = int(os.getenv("PORT", 5000))
print(f"🚀 FASTAPI DEBUG: Railway assigned PORT: {port}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
