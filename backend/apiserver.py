import os
import json
import re
import random
import sanic
import asyncio

app = sanic.Sanic("api-server")


class Game:
    def __init__(self, board=None):
        self.qlock = asyncio.Lock()
        self.current_queues = []

        self.upcoming = 1
        self.theboard = board or {}
        self.hilites = {}
        self.turnmarks = []

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

    def get_meta(self, code):
        return {"code": code, "upcoming": self.upcoming}


GAMES = {}


def create_game(code):
    global GAMES

    gamedir = os.path.join(os.getenv("GAMESDIR"), code)
    metajson = os.path.join(gamedir, "meta.json")
    if os.path.exists(gamedir) and os.path.isfile(metajson):
        raise sanic.exceptions.SanicException(
            "duplicate code generated", status_code=501
        )

    game = Game()
    GAMES[code] = game

    os.mkdir(gamedir)
    with open(metajson, "w") as metafile:
        metafile.write(json.dumps(game.get_meta(code)))

    board = {}
    with open(os.path.join(gamedir, "board.json"), "w") as boardfile:
        boardfile.write(json.dumps(board))

    return GAMES[code]


def get_created_game(code):
    global GAMES

    if code in GAMES:
        return GAMES[code]

    gamedir = os.path.join(os.getenv("GAMESDIR"), code)
    meta = os.path.join(gamedir, "meta.json")
    if not os.path.exists(gamedir) or not os.path.isfile(meta):
        raise sanic.exceptions.NotFound(f"no game with code {code} found")

    board = {}
    with open(os.path.join(gamedir, "board.json"), "r") as boardfile:
        board = json.loads(boardfile.read())

    GAMES[code] = Game(board)
    return GAMES[code]


@app.route("/api/game/<code>/cell-events")
async def get_api_cell_events(request, code):
    game = get_created_game(code)

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

    v = {
        "source": "root",
        "board": game.theboard,
        "hilites": game.hilites,
        "turnmarks": game.turnmarks,
    }
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
    code = generate_code()
    data = {"code": code}
    create_game(code)
    return sanic.response.json(data)


@app.route("/api/game/<code>/probe")
async def get_api_probe_game(request, code):
    code = re.sub("[ -]", "", code)
    if len(code) != 6:
        raise sanic.exceptions.NotFound("game codes must be  numeric characters")

    code = f"{code[:3]}-{code[3:]}"
    get_created_game(code)
    return sanic.response.json({"code": code})


@app.route("/api/game/<code>/cell-shot", methods=["PUT"])
async def put_api_cell_shot(request, code):
    game = get_created_game(code)

    body = request.json
    if "shot" in body:
        # TODO add some defensive validation here?
        game.theboard.update(body["shot"])

        gamedir = os.path.join(os.getenv("GAMESDIR"), code)
        with open(os.path.join(gamedir, "board.json"), "w") as boardfile:
            boardfile.write(json.dumps(game.theboard))

    await game.enqueue(body)
    return sanic.response.json({})


@app.route("/api/game/<code>/complete-turn", methods=["PUT"])
async def put_api_complete_turn(request, code):
    game = get_created_game(code)

    body = request.json
    if "turn" in body:
        game.upcoming = body["turn"] + 1

        gamedir = os.path.join(os.getenv("GAMESDIR"), code)
        with open(os.path.join(gamedir, "meta.json"), "w") as metafile:
            metafile.write(json.dumps(game.get_meta(code)))

    await game.enqueue(body)
    return sanic.response.json({})


@app.route("/api/game/<code>/cell-highlight", methods=["PUT"])
async def put_api_cell_highlight(request, code):
    game = get_created_game(code)

    body = request.json
    if "highlight" in body:
        # TODO add some defensive validation here?
        game.hilites.update(body["highlights"])

    await game.enqueue(body)
    return sanic.response.json({})


@app.route("/api/game/<code>/turn-highlight", methods=["PUT"])
async def put_api_turn_highlight(request, code):
    game = get_created_game(code)

    body = request.json
    if "turnmarks" in body:
        # TODO add some defensive validation here?
        game.turnmarks = body["turnmarks"]

    await game.enqueue(body)
    return sanic.response.json({})


@app.route("/api/ping")
async def get_api_ping(request):
    return sanic.response.text(".")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, auto_reload=True)
