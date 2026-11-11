import { Routes, Route, Link } from "react-router"
import ProductsPage from './pages/ProductsPage.jsx'
import BrowsePage from './pages/BrowsePage.jsx'
import ProductDetailPage from './pages/ProductDetailPage.jsx'

function App() {

  return (
    <>
    <nav>
      <Link to="/">All Products</Link> | <Link to="/browse">Browse</Link>
    </nav>
    <Routes>
      <Route path="/" element={<ProductsPage/>} />
      <Route path="/browse" element={<BrowsePage/>} />
      <Route path="/products/:id" element={<ProductDetailPage/>} />
      <Route path="*" element={<h1>404 Not Found</h1>} />
    </Routes>
    </>
  )
}

export default App
