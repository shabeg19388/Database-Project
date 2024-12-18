import {getQuery} from './getQuery';
import { useState } from 'react';
import { useMutation} from "@tanstack/react-query";

const Form = () => {
    const [newQuery, setNewQuery] = useState('');
    const [data, setData] = useState(null);
    
    const formMutation = useMutation({mutationFn : getQuery, 
        onSuccess : (data) => {
            setData(data)
    }});

    const handleSubmit = (event) => {
        event.preventDefault();
        if(newQuery.trim()){
            formMutation.mutate(newQuery.trim());
        };
        setNewQuery('')
    };

    const search = (
        <form onSubmit = {handleSubmit}>
            <div>
                <label htmlFor='queryInputy'>Enter your english query!</label>
                <input type='text' id = 'query' value = {newQuery} onChange = {(e) => setNewQuery(e.target.value)}></input>
            </div>
            <button type ='submit'>Submit</button>
        </form>
    );

    let content
    if(formMutation.isPending){
        content = (<h1>Sending Query...</h1>)
    }
    else{
        console.log(data)
        console.log(data['gpt'])
    }


    return(
        <main>
            {search}
            {content}
        </main>
    );
};

export default Form;