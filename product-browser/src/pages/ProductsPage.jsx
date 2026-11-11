import { useState, useEffect } from 'react';
import { Link } from 'react-router';


export default function ProductsPage() {
    const[products, setProducts] = useState([]);

    useEffect(() => {
        async function loadProducts(){
            const res = await fetch("https://dummyjson.com/products");
            const data = await res.json();

            setProducts(data.products);
        }
        loadProducts();
    }, []);

    return(
        <>
        <p>Loaded {products.length} products.</p>
        <ul>
            {products.map((product)=>(
                
                <li key={product.id} >
                    <img src={product.thumbnail} ></img>   
                    <h3>{product.title}</h3>
                    {/* price, rating, category */}
                    <p>Price: ${product.price}</p>
                    <p>Rating: {product.rating}</p>
                    <p>Category: {product.category}</p>
                    <p>{product.reviews.length} reviews</p>
                    <Link to={`/products/${product.id}`}>View Details</Link>
                </li>
            ))}
        </ul>
        </>
    );
}
