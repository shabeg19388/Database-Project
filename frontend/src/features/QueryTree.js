import { TreeTable } from "primereact/treetable";
import { Column } from "primereact/column";
//Creates query tree object for each returned SQL query
export const QueryTree = ({data}) => {
    const queries = {'GPT' : data.GPTQuery, 'Gemini' : data.GeminiQuery, 'Gemini + NumCol': data.NumQuery, 'Gemini + NameCol': data.NameQuery, 'Intersection' : data.IntersectionQuery, 'Union': data.UnionQuery}
    const nodes = Object.keys(queries).map((key, i) => ({
        key: i, 
        data: {name: key}, 
        children : [
            {
                key: i+'-0',
                 data : {
                    name : <div style={{whiteSpace : 'pre', marginTop : "-50px", marginLeft: '65px'}}>{queries[key]}</div>}}]
            }
    ))
    return(
        <TreeTable value={nodes} tableStyle={{minWidth : '20rem'}}>
            <Column field = "name" expander></Column>
        </TreeTable >
    )

    
}