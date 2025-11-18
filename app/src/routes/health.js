const express = require('express');
const router = express.Router();

// Эндпоинт здоровья
router.get('/', (req, res) => {
    res.json({
        status: 'healthy',
        container: process.env.HOSTNAME || 'unknown'
    });
});

module.exports = router;