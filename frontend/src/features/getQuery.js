// Performs fetch function for the backend enpoint. Interacts with Mutation in fronntend to only query when form is submitted
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