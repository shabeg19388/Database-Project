export const getQuery = async (query) => {
    const myHeaders = new Headers();
    myHeaders.append('Content-Type', 'application/json');
    const data = await fetch('http://localhost:8000/query', {
        method : 'POST',
        body: JSON.stringify({query}),
        headers : myHeaders
    });
    return await data.json();
};