const express = require('express');
const app = express();

// Middleware
const { requestCounter, errorCounter } = require('./middleware/metrics');
const { loggingMiddleware } = require('./middleware/logging');

// Routes
const apiRoutes = require('./routes/api');
const healthRoutes = require('./routes/health');
const metricsRoutes = require('./routes/metrics');

// Middleware
app.use(loggingMiddleware);
app.use(requestCounter);

// Routes
app.use('/', apiRoutes);
app.use('/health', healthRoutes);
app.use('/metrics', metricsRoutes);

// Error handling
app.use(errorCounter);

module.exports = app;