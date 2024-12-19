import {getQuery} from './getQuery';
import { useState} from 'react';
import { useMutation} from "@tanstack/react-query";
import {Table} from './Table';
import { TabView, TabPanel } from 'primereact/tabview';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import {QueryTree} from './QueryTree'
import { Schema } from './Schema';
import { Accordion, AccordionTab } from 'primereact/accordion';
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
    };

    const search = (
        <form onSubmit = {handleSubmit}>
            <div style={{display : "flex", alignItems : 'center', justifyContent : 'center', marginTop: '30px', marginBottom : '0px'}}>
                <InputText value={newQuery} className="p-inputtext-lg" onChange = {(e) => setNewQuery(e.target.value)} placeholder='Enter an English query!'/>
                <Button label='Submit' loading ={formMutation.isPending}/>
            </div>
        </form>

    );
    
    let content
    if(data){
        console.log(data)
        content = (
            <>
                <Accordion className='queries-accordian'>
                    <AccordionTab header='Queries' className='accord-tab'>
                        <QueryTree data={data}/>
                    </AccordionTab>
                </Accordion>
                <TabView>
                    <TabPanel header='GPT'>
                        <Table data = {data['gpt']} title='gpt'/>
                    </TabPanel>
                    <TabPanel header='Gemini'>
                        <Table data={data['gemini']} title='gemini'/>
                    </TabPanel>
                    <TabPanel header='Gemini + NumCol'>
                        <Table data={data['gemini_num']} title='gemini_num' />
                    </TabPanel>
                    <TabPanel header='Gemini + NameCol'>
                        <Table data={data['gemini_name']} title='gemini_name'/>
                    </TabPanel>
                    <TabPanel header='Intersection'>
                        <Table data={data['intersection']} title='intersection'/>
                    </TabPanel>
                    <TabPanel header='Union'>
                        <Table data={data['union']} title='union'/>
                    </TabPanel>
                </TabView>
            </>
        )
    }

    
    return(
        <main>
            {search}
            <Schema/>
            {content}
        </main>
    );
};

export default Form;