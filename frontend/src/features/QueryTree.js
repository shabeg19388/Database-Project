import { TreeTable } from "primereact/treetable";
import { Column } from "primereact/column";
export const QueryTree = ({data}) => {
    const queries = {'GPT' : data.GPTQuery, 'Gemini' : data.GeminiQuery, 'Gemini + NumCol': data.GeminiNumQuery, 'Gemini + NameCol': data.GeminiNameQuery, 'Intersection' : data.IntersectionQuery, 'Union': data.UnionQuery}
    const nodes = Object.keys(queries).map((key, i) => ({
        key: i, 
        data: {name: key}, 
        children : [
            {
                key: i+'-0',
                 data : {
                    name : <div style={{whiteSpace : 'pre', marginTop : "-30px", marginLeft: '65px'}}>{queries[key]}</div>}}]
            }
    ))
    return(
        <TreeTable value={nodes} tableStyle={{minWidth : '20rem'}}>
            <Column field = "name" expander></Column>
        </TreeTable >
    )

    
}