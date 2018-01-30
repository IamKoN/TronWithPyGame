import pygame
from pygame.locals import *
import pygbutton
import random
#from pygame import *


def Enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


Compass = Enum(NORTH = 0, EAST = 1, SOUTH = 2, WEST = 3)

Color = Enum(RED=(255, 0, 0), BLUE=(0, 0, 255), ORANGE=(255, 180, 0), GREEN=(0, 192, 0), YELLOW=(255, 255, 0),
            PURPLE=(255, 0, 255), CYAN=(0, 255, 255), WHITE=(255, 255, 255), GRAY=(100, 100, 100), BLACK=(0, 0, 0))

class Bike(object):
    def __init__(self, Color, Direction=Compass.NORTH, StartX=0, StartY=0):
        self.TrailColor = Color
        self.Direction = Direction
        self._Trail = [(StartX, StartY)]
        self._Speed = 3

    def Trail(self):
        return self._Trail[:]

    def SetSpeed(self, NewSpeed):
        self._Speed = NewSpeed

    def Move(self):
        # First find the current position.
        currentPosition = self._Trail[-1]

        # Determine direction to move
        if self.Direction == Compass.NORTH:
            self._Trail.append((currentPosition[0], currentPosition[1] - self._Speed))
        elif self.Direction == Compass.EAST:
            self._Trail.append((currentPosition[0] + self._Speed, currentPosition[1]))
        elif self.Direction == Compass.SOUTH:
            self._Trail.append((currentPosition[0], currentPosition[1] + self._Speed))
        else:
            self._Trail.append((currentPosition[0] - self._Speed, currentPosition[1]))

        # Return the light ribbon.
        return self._Trail

    def ChangeDirection(self, newDirection):
        # Check to make sure the bike is not pulling a 180 degree turn.
        if ((self.Direction == Compass.NORTH and newDirection == Compass.SOUTH)
            or (self.Direction == Compass.SOUTH and newDirection == Compass.NORTH)
            or (self.Direction == Compass.EAST and newDirection == Compass.WEST)
            or (self.Direction == Compass.WEST and newDirection == Compass.EAST)):
            pass
        else:
            self.Direction = newDirection

    def HitTrail(self, trail):
        for xyPos in trail:
            if self._Trail.count(xyPos) > 0:
                return True
        return False

    def HitWall(self, xPos, yPos):
        # First find the current position.
        currentPosition = self._Trail[-1]

        return ((currentPosition[0] < 1 or currentPosition[0] >= xPos)
                or (currentPosition[1] < 1 or currentPosition[1] >= yPos)
                or (self._Trail.count(currentPosition) > 1))


class Player(object):
    def __init__(self, pID):
        self._Health = 1
        self._Id = pID
        self.Bike = None

    def LoseHP(self):
        # Decrease health by one.
        self._Health = self._Health - 1
        return self._Health == 0

    def PID(self):
        return self._Id

    def SetPlayerColor(self, Direction, StartX, StartY):
        color = Color.RED
        startDirection = Compass.SOUTH

        if self._Id == 0:
            color = Color.CYAN
            startDirection = Compass.EAST
        elif self._Id == 1:
            color = Color.ORANGE
            startDirection = Compass.WEST
        elif self._Id == 2:
            color = Color.GREEN
        elif self._Id == 3:
            color = Color.YELLOW
        elif self._Id == 4:
            color = Color.WHITE
        self.Bike = Bike(color, Direction, StartX, StartY)


class Arena(object):
    def __init__(self, Width, Height):
        # Initialize the game grid.
        self.Height = Height
        self.Width = Width
        self._FrameRate = 30
        self.allPlayers = []
        
        # Initialize pyGame.
        pygame.init()
        pygame.display.set_caption("Battle Bikes")
        self._Clock = pygame.time.Clock()
        self._Screen = pygame.display.set_mode((self.Width, self.Height))
        self._Background = pygame.Surface(self._Screen.get_size())
        self._Background.fill(Color.BLACK)
        self.randColor = Color.WHITE

        self.running = True
        self.gameOver = False
        self.pause = True
        self.pauseReset = True
        self.visMode = True

        self.loserColor = "A COLOR"
        self.loser = 10
        self.speedTxt = 'test'
        self.gameResult = 'Match in progress'
        # self._Menu = pygame.Surface(self.Width//2, self.Height//10)
        # self._Menu.fill(Color.GRAY)

        self.DownSpeedButton = pygbutton.PygButton((self.Width * 0, 0, self.Width / 5, 30), "Slow Down", Color.GREEN)
        self.UpSpeedButton = pygbutton.PygButton((self.Width * (1 / 5), 0, self.Width / 5, 30), "Speed Up", Color.GREEN)
        self.ContButton = pygbutton.PygButton((self.Width * (2 / 5), 0, self.Width / 5, 30), "Continue", Color.GREEN)
        self.PlayButton = pygbutton.PygButton((self.Width * (3 / 5), 0, self.Width / 5, 30), "New Game", Color.GREEN)
        self.QuitButton = pygbutton.PygButton((self.Width * (4 / 5), 0, self.Width / 5, 30), "Quit", Color.GREEN)
        self.menuButtons = (self.UpSpeedButton, self.DownSpeedButton)
        self.pauseButtons = (self.ContButton, self.QuitButton)
        self.endButtons = (self.PlayButton, self.QuitButton)
        self.allButtons = self.menuButtons + self.pauseButtons + self.endButtons

    def randColor(self):
        self.randColor = [random.randint(0,100) for _ in range(3)]

    def IsRunning(self):
        #return len(self.allPlayers) > 1
        return self.running

    def SetFrameRate(self, Rate):
        self._FrameRate = Rate

    def _DrawTrail(self, Vertices, Color=Color.RED):
        pygame.draw.lines(self._Screen, Color, False, Vertices, 1)

    def _Opponents(self, Player):
        opponents = self.allPlayers[:]
        opponents.remove(Player)
        return opponents

    def InsertPlayer(self, Player):
        self.allPlayers.append(Player)

    def DisplayHandling(self):
        self._Clock.tick(self._FrameRate)
        self._Screen.blit(self._Background, (0, 0))

        for b in self.allButtons:
            b.draw(self._Screen)
            b.visible = self.visMode

        for prog in self.allPlayers:
            self._DrawTrail(prog.Bike.Move(), prog.Bike.TrailColor)

            if prog.Bike.HitWall(self.Width, self.Height):
                if prog.LoseHP():
                    self.loser = prog.PID()
                    self.allPlayers.remove(prog)
            else:
                # For each opponent check if Player hit their trail

                for opponent in self._Opponents(prog):
                    if prog.Bike.HitTrail(opponent.Bike.Trail()):
                        if prog.LoseHP():
                            self.loser = prog.PID()
                            self.allPlayers.remove(prog)
        if self.loser == 0:
            self.loserColor = "CYAN"
        elif self.loser == 1:
            self.loserColor = "ORANGE"

        for e in pygame.event.get():
            #Start/End game menu
            if len(self.allPlayers) < 2:
                #self._Clock.tick(self._FrameRate)
                self.Pause()
                endFont = pygame.font.Font(None, 60)
                gameover = endFont.render(("GAME OVER\n" + self.loserColor + "WINS"), False, (255, 255, 255))
                rect = gameover.get_rect()
                rect.center = self._Screen.get_rect().center
                self._Screen.blit(gameover, rect)
                #pygame.display.flip()


            # Quit
            if (e.type == QUIT) or (e.type == KEYDOWN and e.key == K_ESCAPE):
                self.allPlayers = []
                self.running = False
                pygame.quit()

            #Pause
            if (e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE): # or (e.type == pygame.KEYUP and e.key == pygame.K_SPACE):
                self.Pause()

            #PLayer navigation
            if e.type == KEYDOWN:
                # Player one navigation.
                if e.key == K_a:
                    self.allPlayers[0].Bike.ChangeDirection(Compass.WEST)
                elif e.key == K_s:
                    self.allPlayers[0].Bike.ChangeDirection(Compass.SOUTH)
                elif e.key == K_d:
                    self.allPlayers[0].Bike.ChangeDirection(Compass.EAST)
                elif e.key == K_w:
                    self.allPlayers[0].Bike.ChangeDirection(Compass.NORTH)

                # Player two navigation.
                elif e.key == K_j:
                    self.allPlayers[1].Bike.ChangeDirection(Compass.WEST)
                elif e.key == K_k:
                    self.allPlayers[1].Bike.ChangeDirection(Compass.SOUTH)
                elif e.key == K_l:
                    self.allPlayers[1].Bike.ChangeDirection(Compass.EAST)
                elif e.key == K_i:
                    self.allPlayers[1].Bike.ChangeDirection(Compass.NORTH)

        pygame.display.flip()
    
    def Pause(self):
        while self.pause:
            e = pygame.event.wait()
            # Start/Restart Game
            if 'click' in self.PlayButton.handleEvent(e):
                self.allPlayers = []
                self.running = False
                startGame()
                break

            # Increment speed
            if 'click' in self.UpSpeedButton.handleEvent(e):
                for prog in self.allPlayers:
                    prog.Bike.SetSpeed(prog.Bike._Speed + 1)
            if 'click' in self.DownSpeedButton.handleEvent(e):
                for prog in self.allPlayers:
                    prog.Bike.SetSpeed(prog.Bike._Speed - 1)

            # Resume
            if 'click' in self.ContButton.handleEvent(e) or (e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE):
                # self.visMode = not self.visMode
                # self.pause = not self.pause
                break

            # Quit
            if (e.type == QUIT) or (e.type == KEYDOWN and e.key == K_ESCAPE) or (
                        'click' in self.QuitButton.handleEvent(e)):
                self._Players = []
                self.running = False
                pygame.quit()

def startGame():
    newArena = Arena(800, 560)
    newArena.SetFrameRate(30)

    # Create the players

    p1 = Player(0)
    p1.SetPlayerColor(Compass.EAST, 10, newArena.Height/2)

    p2 = Player(1)
    p2.SetPlayerColor(Compass.WEST, newArena.Width - 10, newArena.Height/2)

    newArena.InsertPlayer(p1)
    newArena.InsertPlayer(p2)

    while newArena.IsRunning():
        newArena.DisplayHandling()

if __name__ == "__main__":
    startGame()
