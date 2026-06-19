const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const comboEl = document.getElementById('combo');
const livesEl = document.getElementById('lives');
const levelEl = document.getElementById('level');
const activeCountEl = document.getElementById('activeCount');
const messageEl = document.getElementById('message');
const startButton = document.getElementById('startButton');
const difficultySelect = document.getElementById('difficulty');
const leaderboardList = document.getElementById('leaderboardList');
const resetRankingButton = document.getElementById('resetRanking');

let gameState = 'stopped';
let score = 0;
let combo = 0;
let lives = 3;
let level = 1;
let hitsThisLevel = 0;
let speed = 2.2;
let lastFrame = 0;
let animationId = null;
let spawnTimer = 0;
let spawnInterval = 1;
let activeTargets = [];
let particles = [];
let popups = [];
let hitSound, missSound, uiSound;

const sujiImageNames = [
  '이미지/0.jpg',
  '이미지/01_38866.jpg',
  '이미지/06_39958.jpg',
  '이미지/1-.jpg',
  '이미지/1-1.jpg',
  '이미지/1-2.jpg',
  '이미지/1-모바일.jpg',
  '이미지/11.jpg',
  '이미지/111.jpg',
  '이미지/1111.jpg',
  '이미지/11111.jpg',
  '이미지/111111.jpg',
  '이미지/11번가_겨울.jpg',
  '이미지/11번가_겨울1.jpg',
  '이미지/800.jpg',
  '이미지/퀸잇_250217.jpg',
];
const hyeonjinImageNames = [
  '현진/08-1511-Wide.jpg',
  '현진/08-1582.jpg',
  '현진/08-1615.jpg',
  '현진/11-2026-Wide.jpg',
  '현진/11-2086.jpg',
  '현진/12-2106.jpg',
  '현진/12-2212.jpg',
  '현진/12-2293.jpg',
  '현진/12-2341.jpg',
];
const characterImages = [];
let loadedCharacterImages = 0;

const config = {
  maxLives: 3,
  baseRadius: 46,
  hitBonus: 12,
  comboBonus: 2,
  speedIncrease: 0.16,
  missPenalty: 1,
};

const difficultySettings = {
  easy: {
    speed: 1.5,
    hitBonus: 8,
    comboBonus: 1,
    maxLives: 4,
    minRadius: 52,
    maxRadius: 72,
    maxTargets: 3,
    spawnInterval: 1.3,
  },
  normal: {
    speed: 2.2,
    hitBonus: 12,
    comboBonus: 2,
    maxLives: 3,
    minRadius: 38,
    maxRadius: 58,
    maxTargets: 4,
    spawnInterval: 0.95,
  },
  hard: {
    speed: 3.0,
    hitBonus: 16,
    comboBonus: 3,
    maxLives: 2,
    minRadius: 28,
    maxRadius: 46,
    maxTargets: 5,
    spawnInterval: 0.75,
  },
};

function loadSounds() {
  hitSound = new Audio();
  hitSound.src = 'data:audio/wav;base64,UklGRhIAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA=';
  missSound = new Audio();
  missSound.src = 'data:audio/wav;base64,UklGRgIAAABXQVZFZm10IBAAAAABAAEAQB8AAIA/AAACABAAZGF0YQAAAAA=';
  uiSound = new Audio();
  uiSound.src = 'data:audio/wav;base64,UklGRgQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA/AAACABAAZGF0YQAAAAA=';
}
function loadCharacterImages() {
  sujiImageNames.forEach(src => {
    const img = new Image();
    img.src = src;
    img.onload = () => {
      loadedCharacterImages += 1;
    };
    img.onerror = () => {
      console.warn('이미지 로딩 실패:', src);
      loadedCharacterImages += 1;
    };
    characterImages.push({ image: img, isHyeonjin: false });
  });

  hyeonjinImageNames.forEach(src => {
    const img = new Image();
    img.src = src;
    img.onload = () => {
      loadedCharacterImages += 1;
    };
    img.onerror = () => {
      console.warn('이미지 로딩 실패:', src);
      loadedCharacterImages += 1;
    };
    characterImages.push({ image: img, isHyeonjin: true });
  });
}
function playSound(sound) {
  if (!sound) return;
  sound.currentTime = 0;
  sound.play().catch(() => {});
}

function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * window.devicePixelRatio;
  canvas.height = rect.height * window.devicePixelRatio;
  ctx.setTransform(window.devicePixelRatio, 0, 0, window.devicePixelRatio, 0, 0);
}

function getDifficultyConfig() {
  return difficultySettings[difficultySelect.value] || difficultySettings.normal;
}

function resetGame() {
  const difficulty = getDifficultyConfig();
  score = 0;
  combo = 0;
  level = 1;
  hitsThisLevel = 0;
  lives = difficulty.maxLives;
  speed = difficulty.speed;
  config.hitBonus = difficulty.hitBonus;
  config.comboBonus = difficulty.comboBonus;
  spawnTimer = 0;
  spawnInterval = difficulty.spawnInterval;
  activeTargets = [];
  particles = [];
  popups = [];
  for (let i = 0; i < 2; i += 1) {
    spawnTarget();
  }
  updateStats();
  messageEl.textContent = '빠르게 터치해서 콤보를 쌓아보세요!';
  messageEl.style.opacity = '0.9';
  playSound(uiSound);
}

function startGame() {
  if (gameState === 'playing') return;
  gameState = 'playing';
  resetGame();
  lastFrame = performance.now();
  messageEl.style.opacity = '0';
  if (animationId) cancelAnimationFrame(animationId);
  animationId = requestAnimationFrame(gameLoop);
}

function gameOver() {
  gameState = 'over';
  messageEl.textContent = `게임 종료! 점수 ${score}점. 다시 시작하려면 버튼을 눌러주세요.`;
  messageEl.style.opacity = '0.95';
  saveRanking(score);
  renderLeaderboard();
  playSound(missSound);
  if (animationId) cancelAnimationFrame(animationId);
}

function createTarget() {
  const difficulty = getDifficultyConfig();
  const radius = difficulty.minRadius + Math.random() * (difficulty.maxRadius - difficulty.minRadius);
  const padding = radius + 16;
  const x = padding + Math.random() * (canvas.clientWidth - padding * 2);
  const chosen = characterImages.length ? characterImages[Math.floor(Math.random() * characterImages.length)] : null;
  return {
    x,
    y: -radius,
    radius,
    speed: difficulty.speed + Math.random() * 0.8,
    image: chosen ? chosen.image : null,
    isHyeonjin: chosen ? chosen.isHyeonjin : false,
  };
}

function spawnTarget() {
  const difficulty = getDifficultyConfig();
  if (activeTargets.length >= difficulty.maxTargets) return;
  activeTargets.push(createTarget());
}

function update(dt) {
  if (gameState !== 'playing') return;
  spawnTimer += dt;
  if (spawnTimer >= spawnInterval) {
    spawnTimer -= spawnInterval;
    spawnTarget();
  }
  activeTargets.forEach(target => {
    target.y += target.speed * dt;
  });
  for (let i = activeTargets.length - 1; i >= 0; i -= 1) {
    const target = activeTargets[i];
    if (target.y - target.radius > canvas.clientHeight) {
      activeTargets.splice(i, 1);
      loseLife();
    }
  }
  popups.forEach(popup => {
    popup.age += dt;
    popup.y -= 16 * dt;
    popup.alpha = Math.max(0, 1 - popup.age * 1.3);
  });
  popups = popups.filter(popup => popup.alpha > 0);
  particles.forEach(particle => {
    particle.x += particle.dx;
    particle.y += particle.dy;
    particle.dy += 0.05;
    particle.alpha -= 0.03;
  });
  particles = particles.filter(particle => particle.alpha > 0);
}

function loseLife() {
  lives -= 1;
  combo = 0;
  updateStats();
  showFlash('#ff4d4d');
  playSound(missSound);
  if (lives <= 0) {
    lives = 0;
    updateStats();
    gameOver();
    return;
  }
}

function addPopup(x, y, text, color) {
  popups.push({ x, y, text, color, alpha: 1, age: 0 });
}

function addParticles(x, y, color) {
  const count = 8;
  for (let i = 0; i < count; i += 1) {
    const angle = Math.random() * Math.PI * 2;
    const speedParticle = 1.5 + Math.random() * 1.8;
    particles.push({
      x,
      y,
      dx: Math.cos(angle) * speedParticle,
      dy: Math.sin(angle) * speedParticle,
      alpha: 1,
      size: 2 + Math.random() * 3,
      color,
    });
  }
}

function hitTarget(index) {
  const target = activeTargets.splice(index, 1)[0];
  if (!target) return;
  if (target.isHyeonjin) {
    const penalty = 20;
    score = Math.max(0, score - penalty);
    combo = 0;
    addPopup(target.x, target.y, `-${penalty}`, '#ff4d4d');
    addParticles(target.x, target.y, '#ff84b0');
    messageEl.textContent = '현진! 점수가 깎였습니다!';
    messageEl.style.opacity = '0.95';
    playSound(missSound);
  } else {
    combo += 1;
    const points = config.hitBonus + combo * config.comboBonus + level * 2;
    score += points;
    hitsThisLevel += 1;
    addPopup(target.x, target.y, `+${points}`, '#7cffb2');
    addParticles(target.x, target.y, '#7cffb2');
    if (hitsThisLevel >= 10) {
      hitsThisLevel = 0;
      level += 1;
      messageEl.textContent = `레벨 업! Lv.${level}`;
      messageEl.style.opacity = '0.95';
      playSound(uiSound);
      spawnInterval = Math.max(0.55, spawnInterval - 0.08);
    }
    playSound(hitSound);
  }
  updateStats();
  spawnTarget();
}

function updateStats() {
  scoreEl.textContent = score;
  comboEl.textContent = combo;
  livesEl.textContent = lives;
  levelEl.textContent = level;
  activeCountEl.textContent = activeTargets.length;
}

function drawTarget(target) {
  const style = target.isHyeonjin ? { borderColor: '#ff6c8d', glow: 'rgba(255, 108, 141, 0.18)' } : { borderColor: '#ffffff88', glow: 'rgba(126, 255, 189, 0.16)' };
  ctx.save();
  ctx.beginPath();
  ctx.arc(target.x, target.y, target.radius + 4, 0, Math.PI * 2);
  ctx.fillStyle = style.glow;
  ctx.fill();
  ctx.restore();

  ctx.save();
  ctx.beginPath();
  ctx.arc(target.x, target.y, target.radius, 0, Math.PI * 2);
  ctx.clip();
  if (target.image && target.image.complete) {
    const ratio = target.image.width / target.image.height;
    const diameter = target.radius * 2.1;
    const drawWidth = diameter;
    const drawHeight = diameter / ratio;
    ctx.drawImage(target.image, target.x - drawWidth / 2, target.y - drawHeight / 2, drawWidth, drawHeight);
  } else {
    ctx.fillStyle = '#fff0e6';
    ctx.fill();
  }
  ctx.restore();

  ctx.strokeStyle = style.borderColor;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(target.x, target.y, target.radius, 0, Math.PI * 2);
  ctx.stroke();
}

function draw() {
  ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
  const background = ctx.createLinearGradient(0, 0, 0, canvas.clientHeight);
  background.addColorStop(0, '#ffe8f1');
  background.addColorStop(1, '#ffd1eb');
  ctx.fillStyle = background;
  ctx.fillRect(0, 0, canvas.clientWidth, canvas.clientHeight);

  activeTargets.forEach(drawTarget);

  popups.forEach(popup => {
    ctx.globalAlpha = popup.alpha;
    ctx.fillStyle = popup.color;
    ctx.font = 'bold 18px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(popup.text, popup.x, popup.y);
    ctx.globalAlpha = 1;
  });

  particles.forEach(particle => {
    ctx.globalAlpha = particle.alpha;
    ctx.fillStyle = particle.color;
    ctx.beginPath();
    ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;
  });
}

function gameLoop(timestamp) {
  const dt = Math.min((timestamp - lastFrame) / 16.67, 2);
  lastFrame = timestamp;
  update(dt);
  draw();
  if (gameState === 'playing') animationId = requestAnimationFrame(gameLoop);
}

function checkHit(x, y) {
  if (gameState !== 'playing') return;
  for (let i = activeTargets.length - 1; i >= 0; i -= 1) {
    const target = activeTargets[i];
    const dx = x - target.x;
    const dy = y - target.y;
    if (Math.sqrt(dx * dx + dy * dy) <= target.radius) {
      hitTarget(i);
      return;
    }
  }
}

function getPointerPos(event) {
  const rect = canvas.getBoundingClientRect();
  const clientX = event.touches ? event.touches[0].clientX : event.clientX;
  const clientY = event.touches ? event.touches[0].clientY : event.clientY;
  return {
    x: clientX - rect.left,
    y: clientY - rect.top,
  };
}

function showFlash(color) {
  const overlay = document.createElement('div');
  overlay.style.position = 'absolute';
  overlay.style.inset = '0';
  overlay.style.background = color;
  overlay.style.opacity = '0.14';
  overlay.style.pointerEvents = 'none';
  overlay.style.borderRadius = '32px';
  document.getElementById('gameArea').appendChild(overlay);
  setTimeout(() => overlay.remove(), 120);
}

function getLeaderboard() {
  const raw = localStorage.getItem('tap-blast-leaderboard') || '[]';
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

function saveRanking(value) {
  const list = getLeaderboard();
  list.push({ score: value, date: new Date().toLocaleDateString() });
  list.sort((a, b) => b.score - a.score);
  localStorage.setItem('tap-blast-leaderboard', JSON.stringify(list.slice(0, 5)));
}

function renderLeaderboard() {
  const list = getLeaderboard();
  leaderboardList.innerHTML = '';
  if (!list.length) {
    const placeholder = document.createElement('li');
    placeholder.textContent = '아직 저장된 랭킹이 없습니다.';
    placeholder.className = 'placeholder';
    leaderboardList.appendChild(placeholder);
    return;
  }
  list.forEach((entry, index) => {
    const item = document.createElement('li');
    item.textContent = `${index + 1}. ${entry.score}점 — ${entry.date}`;
    leaderboardList.appendChild(item);
  });
}

function clearRanking() {
  localStorage.removeItem('tap-blast-leaderboard');
  renderLeaderboard();
}

canvas.addEventListener('pointerdown', event => {
  event.preventDefault();
  const { x, y } = getPointerPos(event);
  if (gameState !== 'playing') return;
  checkHit(x, y);
});

startButton.addEventListener('click', startGame);
resetRankingButton.addEventListener('click', clearRanking);
window.addEventListener('resize', resizeCanvas);

loadSounds();
loadCharacterImages();
resizeCanvas();
renderLeaderboard();
