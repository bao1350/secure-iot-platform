import { useState } from "react";
import { useNavigate } from "react-router-dom";


function Login() {


    const navigate = useNavigate();


    const [email,setEmail] = useState("");

    const [password,setPassword] = useState("");



    async function login(){


        const response = await fetch(

            "http://localhost:8000/login",

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },


                body:JSON.stringify({

                    email,

                    password

                })

            }

        );


        const data = await response.json();


        if(data.access_token){


            localStorage.setItem(

                "token",

                data.access_token

            );


            navigate("/dashboard");


        }

        else{


            alert(data.message);

        }


    }



    return (


        <div className="login-page">


            <header className="top-header">

                <h1>
                    Secure IoT Platform
                </h1>

            </header>



            <div className="login-card">


                <h2>
                    Connexion
                </h2>



                <input

                    type="email"

                    placeholder="Email"

                    value={email}

                    onChange={
                        e=>setEmail(e.target.value)
                    }

                />



                <input

                    type="password"

                    placeholder="Mot de passe"

                    value={password}

                    onChange={
                        e=>setPassword(e.target.value)
                    }

                />



                <button onClick={login}>

                    Se connecter

                </button>



                <button

                    className="register-button"

                    onClick={() => navigate("/register")}

                >

                    Créer un compte

                </button>


            </div>


        </div>


    );

}


export default Login;