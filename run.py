from app import create_app

app = create_app()

if __name__ == "__main__":
    # 本番は `gunicorn -w 4 run:app` などで起動してください
    app.run(debug=True)
