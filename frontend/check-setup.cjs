#!/usr/bin/env node

/**
 * Скрипт проверки настройки фронтенда
 * Запуск: node check-setup.js
 */

const fs = require('fs');
const path = require('path');

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkFile(filePath, description) {
  const exists = fs.existsSync(filePath);
  if (exists) {
    log(`✅ ${description}`, 'green');
  } else {
    log(`❌ ${description} — файл не найден: ${filePath}`, 'red');
  }
  return exists;
}

function checkDirectory(dirPath, description) {
  const exists = fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory();
  if (exists) {
    log(`✅ ${description}`, 'green');
  } else {
    log(`❌ ${description} — папка не найдена: ${dirPath}`, 'red');
  }
  return exists;
}

console.log('\n' + '='.repeat(60));
log('Проверка настройки фронтенда', 'blue');
console.log('='.repeat(60) + '\n');

let allOk = true;

// Проверка конфигурационных файлов
log('📄 Конфигурационные файлы:', 'yellow');
allOk &= checkFile('package.json', 'package.json');
allOk &= checkFile('vite.config.ts', 'vite.config.ts');
allOk &= checkFile('tsconfig.json', 'tsconfig.json');
allOk &= checkFile('tailwind.config.js', 'tailwind.config.js');
allOk &= checkFile('postcss.config.js', 'postcss.config.js');
allOk &= checkFile('.env', '.env');
allOk &= checkFile('index.html', 'index.html');

console.log();

// Проверка структуры src/
log('📁 Структура src/:', 'yellow');
allOk &= checkDirectory('src', 'src/');
allOk &= checkDirectory('src/api', 'src/api/');
allOk &= checkDirectory('src/components', 'src/components/');
allOk &= checkDirectory('src/pages', 'src/pages/');
allOk &= checkDirectory('src/types', 'src/types/');
allOk &= checkDirectory('src/utils', 'src/utils/');
allOk &= checkDirectory('src/hooks', 'src/hooks/');

console.log();

// Проверка ключевых файлов src/
log('🔧 Ключевые файлы:', 'yellow');
allOk &= checkFile('src/main.tsx', 'main.tsx');
allOk &= checkFile('src/App.tsx', 'App.tsx');
allOk &= checkFile('src/index.css', 'index.css');

console.log();

// Проверка API файлов
log('🌐 API файлы:', 'yellow');
allOk &= checkFile('src/api/client.ts', 'client.ts');
allOk &= checkFile('src/api/auth.ts', 'auth.ts');
allOk &= checkFile('src/api/vacancies.ts', 'vacancies.ts');
allOk &= checkFile('src/api/evaluations.ts', 'evaluations.ts');

console.log();

// Проверка компонентов
log('🧩 Компоненты:', 'yellow');
allOk &= checkFile('src/components/Layout.tsx', 'Layout.tsx');
allOk &= checkFile('src/components/ProtectedRoute.tsx', 'ProtectedRoute.tsx');
allOk &= checkFile('src/components/LoadingSpinner.tsx', 'LoadingSpinner.tsx');

console.log();

// Проверка страниц
log('📄 Страницы:', 'yellow');
allOk &= checkFile('src/pages/Login.tsx', 'Login.tsx');
allOk &= checkFile('src/pages/Dashboard.tsx', 'Dashboard.tsx');
allOk &= checkFile('src/pages/Results.tsx', 'Results.tsx');
allOk &= checkFile('src/pages/CandidateDetail.tsx', 'CandidateDetail.tsx');

console.log();

// Проверка node_modules
log('📦 Зависимости:', 'yellow');
const hasNodeModules = checkDirectory('node_modules', 'node_modules/');
if (!hasNodeModules) {
  log('⚠️  Запустите: npm install', 'yellow');
}

console.log();

// Проверка .env
if (fs.existsSync('.env')) {
  const envContent = fs.readFileSync('.env', 'utf8');
  if (envContent.includes('VITE_API_BASE_URL')) {
    log('✅ VITE_API_BASE_URL настроен в .env', 'green');
  } else {
    log('❌ VITE_API_BASE_URL не найден в .env', 'red');
    allOk = false;
  }
}

console.log('\n' + '='.repeat(60));
if (allOk) {
  log('✅ Все проверки пройдены! Проект готов к запуску.', 'green');
  log('\nЗапуск: npm run dev', 'blue');
} else {
  log('❌ Обнаружены проблемы. Проверьте файлы выше.', 'red');
}
console.log('='.repeat(60) + '\n');
