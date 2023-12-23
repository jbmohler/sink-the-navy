import json
import random
import sanic
import asyncio

app = sanic.Sanic("api-server")


class Game:
    def __init__(self):
        self.qlock = asyncio.Lock()
        self.current_queues = []

        self.theboard = {}
        self.hilites = {}

    async def add_queue(self):
        q = asyncio.Queue()
        async with self.qlock:
            self.current_queues.append(q)
        return q

    async def remove_queue(self, q):
        async with self.qlock:
            self.current_queues.remove(q)

    async def enqueue(self, item):
        async with self.qlock:
            for q in self.current_queues:
                await q.put(item)


GAMES = {}


def get_game(code):
    global GAMES

    if code not in GAMES:
        GAMES[code] = Game()
    return GAMES[code]


@app.route("/api/game/<code>/cell-events")
async def get_api_cell_events(request, code):
    game = get_game(code)

    # Content type as defined by
    # https://stackoverflow.com/questions/52098863/whats-the-difference-between-text-event-stream-and-application-streamjson

    # https://html.spec.whatwg.org/multipage/server-sent-events.html#server-sent-events-intro

    response = await request.respond(content_type="text/event-stream")

    index = 1

    async def send_event_object(response, obj):
        nonlocal index
        index += 1
        send = f"""\
data: {json.dumps(obj)}
id: {index}

"""
        # explicitly dis-allow cancellation during this send
        await asyncio.shield(response.send(send))

    async def stream_until(response, q):
        while True:
            try:
                value = await asyncio.wait_for(q.get(), 15)
                await send_event_object(response, value)
            except asyncio.exceptions.TimeoutError:
                await asyncio.shield(response.send(":keepalive\n\n"))

    q = await game.add_queue()

    v = {"source": "root", "board": game.theboard, "hilites": game.hilites}
    await send_event_object(response, v)

    # run for 3*60 seconds
    try:
        await asyncio.wait_for(stream_until(response, q), 3 * 60)
    except asyncio.exceptions.TimeoutError:
        # TimeoutError is working as designed
        pass

    await game.remove_queue(q)

    await response.eof()


@app.route("/")
async def test(request):
    return sanic.response.json({"hello": "world"})


def generate_code():
    digits = f"{random.randint(0, 999999):06n}"
    return f"{digits[:3]}-{digits[3:]}"


@app.route("/api/create-game", methods=["POST"])
async def post_api_create_game(request):
    data = {"code": generate_code()}
    return sanic.response.json(data)


@app.route("/api/probe-game")
async def get_api_probe_game(request):
    return sanic.response.json({"code": request.args.get("code")})


@app.route("/api/game/<code>/cell-shot", methods=["PUT"])
async def put_api_cell_shot(request, code):
    game = get_game(code)

    body = request.json
    if "shot" in body:
        # TODO add some defensive validation here?
        game.theboard.update(body["shot"])

    await game.enqueue(body)
    return sanic.response.json({})


@app.route("/api/ping")
async def get_api_ping(request):
    return sanic.response.text(".")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, auto_reload=True)
