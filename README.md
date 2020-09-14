# P&L Viewer
A lightweight tool to visualize historical P&amp;L

**Run locally**
1. *docker run -p 5006:5006 rochejo/pnlviewer*
2. Open http://localhost:5006/pnlviewer in a browser

**Deployment**
*docker run -p 5006:5006 rochejo/pnlviewer --env BOKEH_ALLOW_WS_ORIGIN={host}*

**Docker Image**
https://hub.docker.com/r/rochejo/pnlviewer