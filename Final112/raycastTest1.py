from cmu_graphics import *
import math
def onAppStart(app):
    resetApp(app)

def resetApp(app):
    app.width = 600
    app.height = 600
    app.board = getGameMap(2)
    app.rows = len(app.board)
    app.cols = len(app.board[0])
    app.cellWidth = app.width/app.cols
    app.cellHeight = app.height/app.rows
    app.paused = False
    app.stepsPerSecond = 60
    
    app.playerX = 300
    app.playerY = 150
    app.playerAngle = math.radians(-90)
    app.playerSize = 8
    app.fovLineLen = 800
    app.fov = math.radians(60)
    app.moveSpeed = 3
    app.rotateSpeed = math.radians(4)
    
    # raycasting
    app.numRays = 120
    app.rayCheckInterval = 1
    app.scaleConstant = 600
    app.is3D = False

def onKeyPress(app, key):
    if key == 'p':
        app.paused = not app.paused

    if key == 't':
        app.is3D = not app.is3D

    if key == 'r':
        resetApp(app)

    if key == 'm':

        resetApp(app)
        
    
def onKeyHold(app, keys):
    if app.paused:
        return
    
    if 'right' in keys:
        app.playerAngle += app.rotateSpeed
        
    if 'left' in keys:
        app.playerAngle -= app.rotateSpeed
    
    dPos = 0
    if 'up' in keys:
        dPos = app.moveSpeed
    if 'down' in keys:
        dPos = -app.moveSpeed
        
    if dPos != 0:
        newX = dPos*math.cos(app.playerAngle) + app.playerX
        newY = dPos*math.sin(app.playerAngle) + app.playerY
        
        oldX = app.playerX
        oldY = app.playerY
        
        app.playerX = newX
        if not isLegalPos(app):
            app.playerX = oldX
        app.playerY = newY
        if not isLegalPos(app):
            app.playerY = oldY
        

def isLegalPos(app):
    if not (0<=app.playerX<=app.width and 0<=app.playerY<=app.height):
        return False
    playerRow, playerCol = getPlayerRowCol(app)
    return app.board[playerRow][playerCol] == 0
    
def getPlayerRowCol(app):
    playerRow = math.floor(app.playerY/app.cellHeight)
    playerCol = math.floor(app.playerX/app.cellWidth)
    if playerRow > app.rows-1:
        playerRow = app.rows-1
    if playerCol > app.cols-1:
        playerCol = app.cols-1
        
    return playerRow, playerCol
    

def getRayRowCol(app, x, y):
    rRow = math.floor(y/app.cellHeight)
    rCol = math.floor(x/app.cellWidth)
    if rRow > app.rows-1:
        rRow = app.rows-1
    if rRow<0:
        rRow = 0
    if rCol > app.cols-1:
        rCol = app.cols-1
    if rCol<0:
        rCol = 0
    return rRow, rCol
    
def castRayDDA(app,angle):
    pass

def castRay(app, angle):
    mult = app.rayCheckInterval
    rayX = app.playerX
    rayY = app.playerY
    rRow, rCol = getRayRowCol(app,rayX,rayY)

    while mult<1000:
        if app.board[rRow][rCol] == 1:
            break
        elif not (0<rayX<app.width and 0<rayY<app.height):
            break
        mult += app.rayCheckInterval
        rayX = app.playerX + mult*math.cos(angle)
        rayY = app.playerY + mult*math.sin(angle)
        rRow, rCol = getRayRowCol(app,rayX,rayY)
    return rayX, rayY
    
def drawAllRays(app):
    halfFOV = app.fov/2
    leftAngle = app.playerAngle - halfFOV
    rayInterval = app.fov/app.numRays
    for i in range(0,app.numRays):
        rayX, rayY = castRay(app, leftAngle+i*rayInterval)
        
        #rayX = app.playerX + app.fovLineLen*math.cos(leftAngle+i*rayInterval)
        #rayY = app.playerY + app.fovLineLen*math.sin(leftAngle+i*rayInterval)
        drawRay(app, rayX, rayY)
        
def drawRay(app, x, y):
    drawLine(app.playerX, app.playerY, x, y, fill = 'white', opacity = 20)
    drawCircle(x, y, 2, fill = 'orange', opacity = 50)
                
    
        
def drawPlayer(app):
    halfFOV = app.fov/2
    leftAngle = app.playerAngle - halfFOV
    rightAngle = app.playerAngle + halfFOV
    
    # sightline
    
    endX, endY = castRay(app, app.playerAngle)
    
    #endX = app.playerX + app.fovLineLen*math.cos(app.playerAngle)
    #endY = app.playerY + app.fovLineLen*math.sin(app.playerAngle)
    
    # fov line endpoints
    lx = app.playerX + app.fovLineLen*math.cos(leftAngle)
    ly = app.playerY + app.fovLineLen*math.sin(leftAngle)
    rx = app.playerX + app.fovLineLen*math.cos(rightAngle)
    ry = app.playerY + app.fovLineLen*math.sin(rightAngle)
    
    
    
    drawCircle(app.playerX, app.playerY, app.playerSize, fill = 'red') #Player
    
    # sight line
    drawLine(app.playerX, app.playerY, endX, endY, 
                    fill = 'yellow', opacity = 50)
    # left line
    drawLine(app.playerX, app.playerY, lx, ly, 
                fill = 'lightBlue', opacity = 30)
    # right line
    drawLine(app.playerX, app.playerY, rx, ry, 
                fill = 'lightBlue', opacity = 30)
                
    drawAllRays(app)

def draw2D(app):
    drawRect(0, 0, app.width, app.height, fill = 'Black', border = 'lightGreen',
             
    borderWidth = 3)
    drawBoard(app)
    drawPlayer(app)

def draw3D(app):
    # 1. Clear Screen (Black()
    drawRect(0, 0, app.width, app.height, fill='brown')
    drawRect(0,app.height/2, app.width, app.height, fill = 'grey')

    # 2. Render 3D Wall Strips (Full Screen)
    halfFOV = app.fov / 2
    startAngle = app.playerAngle - halfFOV
    rayInterval = app.fov / app.numRays
    stripWidth = app.width / app.numRays

    for i in range(app.numRays):
        angle = startAngle + (i * rayInterval)
        hitX, hitY = castRay(app, angle)
        dist = math.dist((app.playerX, app.playerY), (hitX, hitY))
        
        if dist < 1: dist = 1
        lineHeight = (app.cellHeight * app.scaleConstant) / dist
        
        # Draw the 3D wall slice
        drawRect(i * stripWidth, (app.height - lineHeight) / 2, 
                 stripWidth + 1, lineHeight, fill='lightGreen')

    # --- MINI-MAP WIREFRAME (Top Right) ---
    scale = 0.25
    margin = 10
    mapW = app.width * scale
    mapH = app.height * scale
    mapX = app.width - mapW - margin
    mapY = margin

    # Draw the Map Background
    drawRect(mapX, mapY, mapW, mapH, fill='black', border='lightGreen', borderWidth=1)

    # Draw the Grid (Wireframe Style)
    for row in range(app.rows):
        for col in range(app.cols):
            # Same logic as your drawCell/drawBoard
            cellFill = 'lightGreen' if app.board[row][col] == 1 else None
            drawRect(mapX + col * (app.cellWidth * scale),
                     mapY + row * (app.cellHeight * scale),
                     app.cellWidth * scale, app.cellHeight * scale, 
                     fill=cellFill, border='lightGreen', borderWidth=1)

    # Draw Player and Sightline (Wireframe Style)
    pMapX = mapX + (app.playerX * scale)
    pMapY = mapY + (app.playerY * scale)
    
    # Sightline
    endX, endY = castRay(app, app.playerAngle)
    drawLine(pMapX, pMapY, mapX + (endX * scale), mapY + (endY * scale), 
             fill='yellow', opacity=50)
             
    # Player Dot
    drawCircle(pMapX, pMapY, app.playerSize * scale, fill='red')

def redrawAll(app):
    if app.is3D:
        draw3D(app)
    else:
        draw2D(app)
    
    if app.paused:
        drawRect(app.width/2, app.height/2, 250, 100, fill = 'grey', 
        align = 'center', opacity = 80, border = 'black')
        drawLabel('PAUSED',app.width/2,app.height/2, fill = 'white', 
        border = 'black', borderWidth = 1, size = 50)
    pass

def drawBoard(app):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app,row,col,app.board[row][col])
            
def drawCell(app,row,col,boardData):
    cellLeft, cellTop = getCellLeftTop(app,row,col)
    fillType = 'lightGreen' if boardData == 1 else None
    drawRect(cellLeft, cellTop, app.cellWidth, app.cellHeight, fill = fillType,
    border = 'lightGreen', borderWidth = 1)
    
def getCellLeftTop(app, row, col):
    left = col*app.cellWidth
    top = row*app.cellHeight
    return left,top
def setCell(app,row,col):
    app.board[row][col] = 1-app.board[row][col]

def getGameMap(n):
    
    gameMap0 = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0],
                [0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
              
    
    gameMap1 = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
               [0,1,0,0,0,0,0,1,1,0,0,0,0,0,1,0],
               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
               [0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0],
               [0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0],
               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
               [0,1,0,0,0,0,0,1,1,0,0,0,0,0,1,0],
               [0,1,0,0,0,0,0,1,1,0,0,0,0,0,1,0],
               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
               [0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0],
               [0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0],
               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
               [0,1,0,0,0,0,0,1,1,0,0,0,0,0,1,0],
               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
               
    gameMap2 = [[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
                [0,0,1,1,0,0,0,0,0,0,0,1,0,0,0,0],
                [0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
                [0,0,0,0,0,1,0,0,0,0,1,1,1,0,0,0],
                [0,0,0,0,0,1,0,0,0,1,1,1,1,1,0,0],
                [1,1,1,1,1,1,0,0,0,0,1,1,1,0,0,0],
                [0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,1,0,0,0,1,0,0,0,1,1,1,1,1,1],
                [0,0,1,0,0,1,0,0,0,0,0,1,0,0,0,0],
                [0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]]
               
    gameMap3 = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,0,1,1,1,1,1,0,0,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,1],
    [1,0,1,0,1,1,1,1,1,1,1,0,1,0,0,1,0,0,1,0,1,1,1,0,1,1,1,0,1,0,0,1],
    [1,0,1,0,1,0,0,0,0,0,1,0,1,0,0,1,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,1],
    [1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,1,0,1,1,0,0,0,1,1,0,1,1,1,1,0,0,1,1,1,0,0,0,0,0,1,1,1,0,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,0,0,0,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,1],
    [1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,0,0,1,0,1,1,1,1,1,1,0,0,1,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,1,0,0,0,0,1,0,0,1,0,0,1],
    [1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,0,1,0,1,0,1,1,0,1,0,0,1,0,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,1,1,0,1,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,0,0,1],
    [1,0,1,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,1,1,1,1,0,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1],
    [1,0,1,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,1],
    [1,0,1,1,1,0,1,0,0,1,1,1,1,1,0,1,0,0,1,0,1,1,1,0,1,1,1,0,1,0,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,1,0,1,0,0,0,1,0,0,1],
    [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1,0,1,1,1,1,0,1,0,1,0,1,0,1,0,0,1],
    [1,0,1,0,1,0,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0,0,1,0,1,0,1,0,1,0,0,1],
    [1,0,1,0,1,0,1,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,1,0,1,0,1,0,1,0,0,1],
    [1,0,1,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]   

    gameMap4 = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1],
    [1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1],
    [1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,0,0,1,1],
    [1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,0,0,1,1],
    [1,1,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,1],
    [1,1,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,1],
    [1,1,0,0,1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1],
    [1,1,0,0,1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1],
    [1,1,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1],
    [1,1,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,1,0,0,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,1,0,0,1,1,1,1],
    [1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,1],
    [1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,1],
    [1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,1,0,0,1,1],
    [1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,1,0,0,1,1],
    [1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1],
    [1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1],
    [1,1,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,1,1],
    [1,1,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,1,1],
    [1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1],
    [1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1],
    [1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1],
    [1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1],
    [1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1],
    [1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1],
    [1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]

    maps = [gameMap0, gameMap1, gameMap2, gameMap3, gameMap4]        
              
    return maps[n]
    
runApp()