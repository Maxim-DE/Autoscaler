// Middleware для логирования
// const loggingMiddleware = (req, res, next) => {
//     console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
//     next();
// };

// Middleware для логирования
const loggingMiddleware = (req, res, next) => {
    const getClientIp = (req) => {
        const { 
            headers: { 
                'x-forwarded-for': forwardedFor, 
                'x-real-ip': realIp 
            },
            connection: { remoteAddress: connectionRemote },
            socket: { remoteAddress: socketRemote }
        } = req;

        return forwardedFor || 
               realIp || 
               connectionRemote || 
               socketRemote ||
               (req.connection.socket ? req.connection.socket.remoteAddress : null) ||
               'unknown';
    };

    const clientIp = getClientIp(req);
    
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url} - IP: ${clientIp}`);
    next();
};

module.exports = {
    loggingMiddleware
};