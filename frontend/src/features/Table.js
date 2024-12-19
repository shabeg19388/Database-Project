import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';

export const Table = ({data}, title) => {
    const columns = Object.keys(data[0]).map(
        (key) => ({
            field : key,
            header : key
        })
    )

    
    return(
        <DataTable value={data} paginator stripedRows removableSort scrollable rows={10} rowsPerPageOptions = {[5,10,25,50]} tableStyle={{minWidth : '20 rem'}}>
            {columns.map( (col, i) => (
                <Column key={title+'-'+i} field = {col.field} header = {col.header} sortable/>
            ))}
        </DataTable>

    );
}