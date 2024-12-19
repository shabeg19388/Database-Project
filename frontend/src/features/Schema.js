import { TreeTable } from "primereact/treetable";
import { Column } from "primereact/column";
import { Accordion } from "primereact/accordion";
import { AccordionTab } from "primereact/accordion";
export const Schema = () => {
    const nodes = [
        {   
            key : '0',
            data: {name: 'customers'},
            children: [
                {
                    key: '0-0',
                    data: {name: "customer_id"}
                },
                {
                    key: '0-1',
                    data: {name: "customer_unique_id"}
                },
                {
                    key: '0-2',
                    data: {name: "zip_code"}
                },
                {
                    key: '0-3',
                    data: {name: "city"}
                },
                {
                    key: '0-4',
                    data: {name: "state"}
                }
            ]
        },
        {   
            key : '1',
            data: {name: 'orders'},
            children: [
                {
                    key: '1-0',
                    data: {name: "order_id"}
                },
                {
                    key: '1-1',
                    data: {name: "customer_id"}
                },
                {
                    key: '1-2',
                    data: {name: "order_status"}
                },
                {
                    key: '1-3',
                    data: {name: "order_purchase_timestamp"}
                },
                {
                    key: '1-4',
                    data: {name: "order_approved_at"}
                },
                {
                    key: '1-5',
                    data: {name: "order_delivered_carrier_date"}
                },
                {
                    key: '1-6',
                    data: {name: "order_delivered_customer_date"}
                },
                {
                    key: '1-7',
                    data: {name: "order_estimated_delivery_date"}
                }
            ]
        },
        { 
            key : '2',
            data: {name: 'order_payments'},
            children: [
                {
                    key: '2-0',
                    data: {name: "order_id"}
                },
                {
                    key: '2-1',
                    data: {name: "payment_sequential"}
                },
                {
                    key: '2-2',
                    data: {name: "payment_type"}
                },
                {
                    key: '2-3',
                    data: {name: "payment_installments"}
                },
                {
                    key: '2-4',
                    data: {name: "payment_value"}
                }
            ]
        },
        {
            key : '3',
            data: {name: 'order_reviews'},
            children: [
                {
                    key: '3-0',
                    data: {name: "review_id"}
                },
                {
                    key: '3-1',
                    data: {name: "order_id"}
                },
                {
                    key: '3-2',
                    data: {name: "review_score"}
                },
                {
                    key: '3-3',
                    data: {name: "review_comment_title"}
                },
                {
                    key: '3-4',
                    data: {name: "review_comment_message"}
                },
                {
                    key: '3-5',
                    data: {name: "review_creation_date"}
                },
                {
                    key: '3-6',
                    data: {name: "review_answer_timestamp"}
                }
            ]
        },
        {
            key : '4',
            data: {name: 'geolocation'},
            children: [
                {
                    key: '4-0',
                    data: {name: "zip_code"}
                },
                {
                    key: '4-1',
                    data: {name: "lat"}
                },
                {
                    key: '4-2',
                    data: {name: "lang"}
                },
                {
                    key: '4-3',
                    data: {name: "city"}
                },
                {
                    key: '4-4',
                    data: {name: "state"}
                }
            ]
        },
        {
            key : '5',
            data: {name: 'product_category_name_translation'},
            children: [
                {
                    key: '5-0',
                    data: {name: "category_name"}
                },
                {
                    key: '5-1',
                    data: {name: "category_name_english"}
                }
            ]
        },
        {
            key : '6',
            data: {name: 'products'},
            children: [
                {
                    key: '6-0',
                    data: {name: "product_id"}
                },
                {
                    key: '6-1',
                    data: {name: "category_name"}
                },
                {
                    key: '6-2',
                    data: {name: "name_length"}
                },
                {
                    key: '6-3',
                    data: {name: "description_length"}
                },
                {
                    key: '6-4',
                    data: {name: "photo_qty"}
                },
                {
                    key: '6-5',
                    data: {name: "weight_g"}
                },
                {
                    key: '6-6',
                    data: {name: "length_cm"}
                },
                {
                    key: '6-7',
                    data: {name: "height_cm"}
                },
                {
                    key: '6-8',
                    data: {name: "width_cm"}
                }
            ]
        },
        {
  
            key : '7',
            data: {name: 'sellers'},
            children: [
                {
                    key: '7-0',
                    data: {name: "seller_id"}
                },
                {
                    key: '7-1',
                    data: {name: "zip_code"}
                },
                {
                    key: '7-2',
                    data: {name: "city"}
                },
                {
                    key: '7-3',
                    data: {name: "state"}
                }
            ]
        },
        {
            key : '8',
            data: {name: 'order_items'},
            children: [
                {
                    key: '8-0',
                    data: {name: "order_id"}
                },
                {
                    key: '8-1',
                    data: {name: "order_item_id"}
                },
                {
                    key: '8-2',
                    data: {name: "product_id"}
                },
                {
                    key: '8-3',
                    data: {name: "seller_id"}
                },
                {
                    key: '8-4',
                    data: {name: "shipping_limit_date"}
                },
                {
                    key: '8-5',
                    data: {name: "freight_value"}
                }
            ]
        }
        
    ]
        
    

    return(
        <>
             <Accordion className='schema-accordian' activeIndex={[]}>
                <AccordionTab header='Schema' className="accord-tab">
                    <TreeTable className= 'schema-tree' value={nodes} tableStyle={{minWidth : "20rem"}}>
                        <Column field = "name" header = "Schema" expander></Column>
                    </TreeTable>
                </AccordionTab>
            </Accordion>
        </>
       
        
    )
}