const gridElement = document.getElementById('grid');
const scoreElement = document.getElementById('score');
const highScoreElement = document.getElementById('high-score');
const overlay = document.getElementById('overlay');
const overlayTitle = document.getElementById('overlay-title');
const overlayText = document.getElementById('overlay-text');
const startBtn = document.getElementById('start-btn');

// Game constants
const ROWS = 7;
let COLS = 53;
const SPEED = 120; // ms per tick

// Game state
let snake = [];
let direction = { x: 1, y: 0 };
let nextDirection = { x: 1, y: 0 };
let food = null;
let gameInterval = null;
let score = 0;
let highScore = localStorage.getItem('snakeHighScore') || 0;
let isPlaying = false;
let gridData = [];

highScoreElement.textContent = highScore;

// Fetch contributions and initialize grid
async function initGrid() {
    try {
        const res = await fetch('https://github-contributions.vercel.app/api/v1/Privex-chat');
        const data = await res.json();
        
        // Reverse so it's oldest to newest (left to right)
        const contributions = data.contributions.reverse();
        
        // Filter out leap year extra day if needed to fit perfect 7x52/53 grid
        // Actually, let's just chunk them into columns of 7
        COLS = Math.ceil(contributions.length / 7);
        
        // Setup CSS grid columns
        gridElement.style.gridTemplateColumns = `repeat(${COLS}, var(--cell-size))`;
        
        gridData = [];
        
        for (let col = 0; col < COLS; col++) {
            for (let row = 0; row < ROWS; row++) {
                const index = col * 7 + row;
                const cell = document.createElement('div');
                cell.classList.add('cell');
                cell.dataset.x = col;
                cell.dataset.y = row;
                
                if (index < contributions.length) {
                    const level = contributions[index].intensity;
                    if (level > 0) cell.dataset.level = level;
                }
                
                gridElement.appendChild(cell);
                
                if (!gridData[col]) gridData[col] = [];
                gridData[col][row] = cell;
            }
        }
    } catch (e) {
        console.error("Failed to load contributions, using dummy grid", e);
        // Fallback dummy grid
        COLS = 52;
        gridElement.style.gridTemplateColumns = `repeat(${COLS}, var(--cell-size))`;
        for (let col = 0; col < COLS; col++) {
            for (let row = 0; row < ROWS; row++) {
                const cell = document.createElement('div');
                cell.classList.add('cell');
                cell.dataset.x = col;
                cell.dataset.y = row;
                if (Math.random() > 0.8) cell.dataset.level = Math.floor(Math.random() * 4) + 1;
                gridElement.appendChild(cell);
                
                if (!gridData[col]) gridData[col] = [];
                gridData[col][row] = cell;
            }
        }
    }
}

function getCell(x, y) {
    if (x >= 0 && x < COLS && y >= 0 && y < ROWS) {
        return gridData[x][y];
    }
    return null;
}

function spawnFood() {
    let emptyCells = [];
    for (let x = 0; x < COLS; x++) {
        for (let y = 0; y < ROWS; y++) {
            const isSnake = snake.some(segment => segment.x === x && segment.y === y);
            if (!isSnake) emptyCells.push({x, y});
        }
    }
    
    if (emptyCells.length > 0) {
        food = emptyCells[Math.floor(Math.random() * emptyCells.length)];
        getCell(food.x, food.y).classList.add('food');
    }
}

function startGame() {
    // Reset state
    snake.forEach(segment => {
        const cell = getCell(segment.x, segment.y);
        if (cell) {
            cell.classList.remove('snake');
            cell.classList.remove('snake-head');
        }
    });
    
    if (food) {
        getCell(food.x, food.y).classList.remove('food');
    }
    
    snake = [
        {x: 5, y: 3},
        {x: 4, y: 3},
        {x: 3, y: 3}
    ];
    direction = {x: 1, y: 0};
    nextDirection = {x: 1, y: 0};
    score = 0;
    scoreElement.textContent = score;
    isPlaying = true;
    
    overlay.classList.add('hidden');
    
    snake.forEach((segment, i) => {
        const cell = getCell(segment.x, segment.y);
        cell.classList.add('snake');
        if (i === 0) cell.classList.add('snake-head');
    });
    
    spawnFood();
    
    if (gameInterval) clearInterval(gameInterval);
    gameInterval = setInterval(gameLoop, SPEED);
}

function gameOver() {
    isPlaying = false;
    clearInterval(gameInterval);
    
    if (score > highScore) {
        highScore = score;
        localStorage.setItem('snakeHighScore', highScore);
        highScoreElement.textContent = highScore;
    }
    
    overlayTitle.textContent = "Game Over!";
    overlayText.textContent = `You scored ${score}. Try again?`;
    overlay.classList.remove('hidden');
}

function gameLoop() {
    direction = nextDirection;
    const head = snake[0];
    const newHead = { x: head.x + direction.x, y: head.y + direction.y };
    
    // Check collisions (walls)
    if (newHead.x < 0 || newHead.x >= COLS || newHead.y < 0 || newHead.y >= ROWS) {
        gameOver();
        return;
    }
    
    // Check collisions (self)
    if (snake.some(segment => segment.x === newHead.x && segment.y === newHead.y)) {
        gameOver();
        return;
    }
    
    // Move snake
    snake.unshift(newHead);
    const newHeadCell = getCell(newHead.x, newHead.y);
    newHeadCell.classList.add('snake');
    newHeadCell.classList.add('snake-head');
    
    const oldHeadCell = getCell(head.x, head.y);
    oldHeadCell.classList.remove('snake-head');
    
    // Check food
    if (newHead.x === food.x && newHead.y === food.y) {
        score += 10;
        scoreElement.textContent = score;
        newHeadCell.classList.remove('food');
        spawnFood();
    } else {
        const tail = snake.pop();
        getCell(tail.x, tail.y).classList.remove('snake');
    }
}

// Input handling
window.addEventListener('keydown', e => {
    if (!isPlaying) {
        if (e.key === 'Enter' || e.key === ' ') {
            if (!overlay.classList.contains('hidden')) {
                startGame();
            }
        }
        return;
    }
    
    // Prevent default scrolling for arrow keys and space
    if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "].includes(e.key)) {
        e.preventDefault();
    }
    
    switch (e.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
            if (direction.y === 0) nextDirection = { x: 0, y: -1 };
            break;
        case 'ArrowDown':
        case 's':
        case 'S':
            if (direction.y === 0) nextDirection = { x: 0, y: 1 };
            break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
            if (direction.x === 0) nextDirection = { x: -1, y: 0 };
            break;
        case 'ArrowRight':
        case 'd':
        case 'D':
            if (direction.x === 0) nextDirection = { x: 1, y: 0 };
            break;
    }
});

startBtn.addEventListener('click', startGame);

// Initialize
initGrid();
