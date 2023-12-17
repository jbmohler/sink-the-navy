import sanic

app = sanic.Sanic("api-server")


@app.route("/")
async def test(request):
    return sanic.response.json({"hello": "world"})


@app.route("/api/probe-game")
async def get_api_probe_game(request):
    return sanic.response.json({"code": request.args.get("code")})


@app.route("/api/ping")
async def get_api_ping(request):
    return sanic.response.text(".")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, auto_reload=True)
