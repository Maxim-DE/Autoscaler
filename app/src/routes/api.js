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