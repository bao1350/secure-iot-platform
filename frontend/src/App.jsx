import { BrowserRouter, Routes, Route } from "react-router-dom";

import Auth from "./components/Auth";
import Dashboard from "./components/Dashboard";

import "./App.css";


function App() {


    return (

        <BrowserRouter>


            <Routes>


                <Route

                    path="/"

                    element={<Auth />}

                />


                <Route

                    path="/dashboard"

                    element={<Dashboard />}

                />


            </Routes>


        </BrowserRouter>

    );

}


export default App;