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