function formatDateToUserTimezone(isoString, format = 'datetime') {
    const date = new Date(isoString);
    const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    if (format === 'date') {
        return date.toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            timeZone: userTimeZone
        });
    } else if (format === 'time') {
        return date.toLocaleTimeString(undefined, {
            hour: '2-digit',
            minute: '2-digit',
            timeZone: userTimeZone
        });
    } else {
        return date.toLocaleString(undefined, options);
    }
}