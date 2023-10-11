from random import randint


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutOfBounds(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы доски!"


class BoardUsedCell(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class InvalidShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, length, orientation):
        self.bow = bow
        self.length = length
        self.orientation = orientation
        self.lives = length

    @property
    def cells(self):
        ship_cells = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.orientation == 0:
                cur_x += i

            elif self.orientation == 1:
                cur_y += i

            ship_cells.append(Point(cur_x, cur_y))

        return ship_cells

    def is_hit(self, shot):
        return shot in self.cells


class GameBoard:
    def __init__(self, hidden=False, size=6):
        self.size = size
        self.hidden = hidden

        self.hits = 0

        self.grid = [["O"] * size for _ in range(size)]

        self.used_cells = []
        self.ships = []

    def add_ship(self, ship):

        for cell in ship.cells:
            if self.out_of_bounds(cell) or cell in self.used_cells:
                raise InvalidShipException()
        for cell in ship.cells:
            self.grid[cell.x][cell.y] = "■"
            self.used_cells.append(cell)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, show=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for cell in ship.cells:
            for dx, dy in near:
                cur = Point(cell.x + dx, cell.y + dy)
                if not self.out_of_bounds(cur) and cur not in self.used_cells:
                    if show:
                        self.grid[cur.x][cur.y] = "."
                    self.used_cells.append(cur)

    def __str__(self):
        result = ""
        result += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.grid):
            result += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hidden:
            result = result.replace("■", "O")
        return result

    def out_of_bounds(self, cell):
        return not (0 <= cell.x < self.size) or not (0 <= cell.y < self.size)

    def shoot(self, cell):
        if self.out_of_bounds(cell):
            raise BoardOutOfBounds()

        if cell in self.used_cells:
            raise BoardUsedCell()

        self.used_cells.append(cell)

        for ship in self.ships:
            if cell in ship.cells:
                ship.lives -= 1
                self.grid[cell.x][cell.y] = "X"
                if ship.lives == 0:
                    self.hits += 1
                    self.contour(ship, show=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.grid[cell.x][cell.y] = "Т"
        print("Мимо!")
        return False

    def reset(self):
        self.used_cells = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def make_move(self):
        raise NotImplementedError()

    def play(self):
        while True:
            try:
                target = self.make_move()
                repeat = self.enemy.shoot(target)
                return repeat
            except BoardException as e:
                print(e)


class AIPlayer(Player):
    def make_move(self):
        x = randint(0, 5)
        y = randint(0, 5)
        print(f"Ход компьютера: {x + 1} {y + 1}")
        return Point(x, y)


class HumanPlayer(Player):
    def make_move(self):
        while True:
            coordinates = input("Ваш ход: ").split()

            if len(coordinates) != 2:
                print("Введите 2 координаты!")
                continue

            x, y = coordinates

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue

            x, y = int(x), int(y)

            return Point(x - 1, y - 1)


class BattleshipGame:
    def __init__(self, size=6):
        self.size = size
        player_board = self.create_random_board()
        computer_board = self.create_random_board()
        computer_board.hidden = True

        self.ai = AIPlayer(computer_board, player_board)
        self.user = HumanPlayer(player_board, computer_board)

    def create_random_board(self):
        board = None
        while board is None:
            board = self.place_ships_randomly()
        return board

    def place_ships_randomly(self):
        ship_lengths = [3, 2, 2, 1, 1, 1, 1]
        board = GameBoard(size=self.size)
        attempts = 0
        for length in ship_lengths:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                x = randint(0, self.size - 1)
                y = randint(0, self.size - 1)
                orientation = randint(0, 1)
                ship = Ship(Point(x, y), length, orientation)
                try:
                    # Проверяем, что корабль не касается других кораблей
                    for other_ship in board.ships:
                        for cell in ship.cells:
                            if cell in other_ship.cells:
                                raise InvalidShipException()
                    board.add_ship(ship)
                    break
                except InvalidShipException:
                    pass
        board.reset()
        return board

    def place_ships_randomly(self):
        ship_lengths = [3, 2, 2, 1, 1, 1, 1]
        board = GameBoard(size=self.size)
        attempts = 0
        for length in ship_lengths:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Point(randint(0, self.size - 1), randint(0, self.size - 1)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except InvalidShipException:
                    pass
        board.reset()
        return board

    def greet(self):
        print("Формат ввода: x y")
        print("x - номер строки")
        print("y - номер столбца")

    def play(self):
        self.greet()
        num = 0
        while True:
            print("-" * 20)
            print("Доска игрока:")
            print(self.user.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)

            if num % 2 == 0:
                print("-" * 20)
                print("Ходит игрок!")
                repeat = self.user.play()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.play()

            if repeat:
                num -= 1

            if self.ai.board.hits == 7:
                print("-" * 20)
                print("Игрок выиграл!")
                break

            if self.user.board.hits == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1


if __name__ == "__main__":
    game = BattleshipGame()
    game.play()
