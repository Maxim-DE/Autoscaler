const express = require('express');
const router = express.Router();

// Главная страница
router.get('/', (req, res) => {
    res.json({
        message: 'Привет! Я работаю!',
        container: process.env.HOSTNAME || 'unknown',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// Эндпоинт для простой нагрузки на CPU (вычисление простых чисел)
router.get('/cpu-prime', (req, res) => {
    const limit = parseInt(req.query.limit) || 1000000; // До какого числа искать простые числа
    const duration = parseInt(req.query.duration) || 1000; // Максимальное время работы
    
    console.log(`Поиск простых чисел до ${limit} (макс. ${duration}мс)`);
    
    try {
        const startTime = Date.now();
        
        // Функция проверки числа на простоту
        const isPrime = (num) => {
            if (num <= 1) return false;
            if (num <= 3) return true;
            if (num % 2 === 0 || num % 3 === 0) return false;
            
            let i = 5;
            while (i * i <= num) {
                if (num % i === 0 || num % (i + 2) === 0) return false;
                i += 6;
            }
            return true;
        };
        
        // Находим простые числа
        const primes = [];
        let current = 2;
        let iterations = 0;
        
        while (current <= limit && (Date.now() - startTime) < duration) {
            if (isPrime(current)) {
                primes.push(current);
            }
            current++;
            iterations++;
        }
        
        const actualDuration = Date.now() - startTime;
        const cpuTime = process.cpuUsage();
        
        res.json({
            message: `Выполнено ${iterations} проверок за ${actualDuration}мс`,
            primesFound: primes.length,
            limit: limit,
            maxDuration: `${duration} мс`,
            actualDuration: `${actualDuration} мс`,
            container: process.env.HOSTNAME || 'unknown',
            iterations: iterations,
            lastPrime: primes.length > 0 ? primes[primes.length - 1] : null,
            cpuUsage: {
                user: `${Math.round(cpuTime.user / 1000)} мс`,
                system: `${Math.round(cpuTime.system / 1000)} мс`
            }
        });
        
        console.log(`Найдено ${primes.length} простых чисел за ${actualDuration}мс`);
        
    } catch (error) {
        console.error('Ошибка в вычислениях:', error.message);
        res.status(500).json({
            error: 'Ошибка создания CPU нагрузки',
            message: error.message,
            container: process.env.HOSTNAME || 'unknown'
        });
    }
});

// Эндпоинт для создания нагрузки на память быстрая не большая нагрузка jmetr нагрузит! 
router.get('/memory-fast-heavy', (req, res) => {
    const size = parseInt(req.query.size) || 1; // Размер в МБ (по умолчанию 100 МБ)
    const duration = parseInt(req.query.duration) || 1500; // Время удержания в мс (по умолчанию 10 сек)
    
    console.log(`Выделение ${size} МБ памяти на ${duration} мс`);
    
    try {
        // Создаем большой массив для потребления памяти
        // Каждый элемент ~8 байт (число в JS)
        const arraySize = Math.floor((size * 1024 * 1024) / 8);
        const memoryBlock = new Array(arraySize);
        
        // Заполняем массив данными
        for (let i = 0; i < arraySize; i++) {
            memoryBlock[i] = Math.random();
        }
        
        const memoryUsage = process.memoryUsage();
        
        res.json({
            message: `Выделено ~${size} МБ памяти`,
            duration: `${duration} мс`,
            container: process.env.HOSTNAME || 'unknown',
            memoryUsage: {
                rss: `${Math.round(memoryUsage.rss / 1024 / 1024)} МБ`,
                heapTotal: `${Math.round(memoryUsage.heapTotal / 1024 / 1024)} МБ`,
                heapUsed: `${Math.round(memoryUsage.heapUsed / 1024 / 1024)} МБ`,
                external: `${Math.round(memoryUsage.external / 1024 / 1024)} МБ`
            },
            arraySize: arraySize,
            note: 'Память будет освобождена через ' + duration + ' мс'
        });
        
        // Освобождаем память через указанное время
        setTimeout(() => {
            memoryBlock.length = 0; // Помогаем GC
            console.log(`Память освобождена в контейнере ${process.env.HOSTNAME}`);
        }, duration);
        
    } catch (error) {
        console.error('Ошибка выделения памяти:', error.message);
        res.status(500).json({
            error: 'Не удалось выделить память',
            message: error.message,
            container: process.env.HOSTNAME || 'unknown'
        });
    }
});

// Эндпоинт для создания нагрузки на память
router.get('/memory-heavy', (req, res) => {
    const size = parseInt(req.query.size) || 100; // Размер в МБ (по умолчанию 100 МБ)
    const duration = parseInt(req.query.duration) || 30000; // Время удержания в мс (по умолчанию 10 сек)
    
    console.log(`Выделение ${size} МБ памяти на ${duration} мс`);
    
    try {
        // Создаем большой массив для потребления памяти
        // Каждый элемент ~8 байт (число в JS)
        const arraySize = Math.floor((size * 1024 * 1024) / 8);
        const memoryBlock = new Array(arraySize);
        
        // Заполняем массив данными
        for (let i = 0; i < arraySize; i++) {
            memoryBlock[i] = Math.random();
        }
        
        const memoryUsage = process.memoryUsage();
        
        res.json({
            message: `Выделено ~${size} МБ памяти`,
            duration: `${duration} мс`,
            container: process.env.HOSTNAME || 'unknown',
            memoryUsage: {
                rss: `${Math.round(memoryUsage.rss / 1024 / 1024)} МБ`,
                heapTotal: `${Math.round(memoryUsage.heapTotal / 1024 / 1024)} МБ`,
                heapUsed: `${Math.round(memoryUsage.heapUsed / 1024 / 1024)} МБ`,
                external: `${Math.round(memoryUsage.external / 1024 / 1024)} МБ`
            },
            arraySize: arraySize,
            note: 'Память будет освобождена через ' + duration + ' мс'
        });
        
        // Освобождаем память через указанное время
        setTimeout(() => {
            memoryBlock.length = 0; // Помогаем GC
            console.log(`Память освобождена в контейнере ${process.env.HOSTNAME}`);
        }, duration);
        
    } catch (error) {
        console.error('Ошибка выделения памяти:', error.message);
        res.status(500).json({
            error: 'Не удалось выделить память',
            message: error.message,
            container: process.env.HOSTNAME || 'unknown'
        });
    }
});

// Эндпоинт для создания нагрузки на CPU
router.get('/heavy', (req, res) => {
    let result = 0;
    
    // Простая математическая нагрузка
    for (let i = 0; i < 1000000; i++) {
        result += Math.sqrt(i) * Math.sin(i);
    }
    
    res.json({
        message: 'CPU нагрузка завершена',
        result: result,
        container: process.env.HOSTNAME || 'unknown'
    });
});

// Эндпоинт с задержкой (имитация БД)
router.get('/slow', (req, res) => {
    const delay = parseInt(req.query.delay) || 1000;
    
    setTimeout(() => {
        res.json({
            message: 'Медленный запрос завершен',
            delay: delay + 'ms',
            container: process.env.HOSTNAME || 'unknown'
        });
    }, delay);
});

module.exports = router;