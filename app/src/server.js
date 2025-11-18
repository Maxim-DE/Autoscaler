const app = require('./app');
const PORT = process.env.PORT || 4000;

app.listen(PORT, '0.0.0.0', () => {
    console.log(`✅ Сервер запущен на порту ${PORT}`);
    console.log(`🐳 Контейнер: ${process.env.HOSTNAME || 'unknown'}`);
});