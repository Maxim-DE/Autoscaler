// Счетчики для метрик
let requestCount = 0;
let errorCount = 0;

// Middleware для подсчета запросов
const requestCounter = (req, res, next) => {
    requestCount++;
    next();
};

// Middleware для подсчета ошибок
const errorCounter = (err, req, res, next) => {
    errorCount++;
    console.error('Ошибка:', err);
    res.status(500).json({ error: 'Что-то сломалось!' });
};

module.exports = {
    requestCounter,
    errorCounter,
    getRequestCount: () => requestCount,
    errorCount: () => errorCount
};