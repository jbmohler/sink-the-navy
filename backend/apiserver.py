import json
import sanic
import asyncio

app = sanic.Sanic("api-server")

theboard = {}
hilites = {}

qlock = asyncio.Lock()
current_queues = []


async def add_queue():
    q = asyncio.Queue()
    async with qlock:
        current_queues.append(q)
    return q


async def remove_queue(q):
    async with qlock:
        current_queues.remove(q)


async def enqueue(item):
    async with qlock:
        for q in current_queues:
            await q.put(item)


@app.route("/api/cell-events")
async def get_api_cell_events(request):
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
            value = await q.get()
            await send_event_object(response, value)

    q = await add_queue()

    v = {"board": theboard, "hilites": hilites}
    await send_event_object(response, v)

    # run for 3*60 seconds
    try:
        await asyncio.wait_for(stream_until(response, q), 3 * 6)
    except asyncio.exceptions.TimeoutError:
        # TimeoutError is working as designed
        pass

    await remove_queue(q)

    await response.eof()


@app.route("/")
async def test(request):
    return sanic.response.json({"hello": "world"})


@app.route("/api/probe-game")
async def get_api_probe_game(request):
    return sanic.response.json({"code": request.args.get("code")})


@app.route("/api/cell-shot", methods=["PUT"])
async def put_api_cell_shot(request):
    await enqueue(request.json)
    return sanic.response.json({})


@app.route("/api/ping")
async def get_api_ping(request):
    return sanic.response.text(".")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, auto_reload=True)
