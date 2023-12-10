# Introduction

Sink the Navy is battleship but simply better.

# Backend Service

Backend service is intended to do multi-player game serving perhaps eventually
but first to do screen-share to a large screen monitor.

# Angular Component Notes

Here are some notes about how the angular service was set up and components can
be added.

* See the angular dockerfile where we also specify the user

```shell
$ docker run -it --rm -u 1000:1000 -v ${PWD}/frontend:/app -w /app node:18 bash
root@f024766e6637:/frontend# ls
README.md  angular.json  node_modules  package-lock.json  package.json  src  tsconfig.app.json  tsconfig.json  tsconfig.spec.json
root@f024766e6637:/frontend# npm install -g @angular/cli
...

root@f024766e6637:/frontend# npx ng g component --standalone --skip-tests --dry-run game
CREATE src/app/game/game.component.scss (0 bytes)
CREATE src/app/game/game.component.html (20 bytes)
CREATE src/app/game/game.component.ts (294 bytes)

