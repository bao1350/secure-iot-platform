import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login as apiLogin, register as apiRegister } from "../api/auth";


function Auth() {

    const navigate = useNavigate();

    const [loginEmail, setLoginEmail] = useState("");
    const [loginPassword, setLoginPassword] = useState("");

    const [registerEmail, setRegisterEmail] = useState("");
    const [registerPassword, setRegisterPassword] = useState("");


    async function login() {

        const response = await apiLogin(loginEmail, loginPassword);
        const data = await response.json();

        if (response.ok) {
            navigate("/dashboard");

        }
        else {

            alert(data.detail || "Identifiants invalides");

        }

    }


    async function register() {

        const response = await apiRegister(registerEmail, registerPassword);
        const data = await response.json();

        if (response.status === 200) {

            alert("Compte créé avec succès");
            setRegisterEmail("");
            setRegisterPassword("");

        }
        else {

            alert(data.detail || "Erreur lors de l'inscription");

        }

    }


    return (

        <div className="login-page">

            <header className="top-header">
                <h1>Secure IoT Platform</h1>
            </header>

            <div className="auth-container">

                <div className="login-card">
                    <h2>Connexion</h2>

                    <input
                        type="email"
                        placeholder="Email"
                        value={loginEmail}
                        onChange={e => setLoginEmail(e.target.value)}
                    />

                    <input
                        type="password"
                        placeholder="Mot de passe"
                        value={loginPassword}
                        onChange={e => setLoginPassword(e.target.value)}
                    />

                    <button onClick={login}>
                        Se connecter
                    </button>
                </div>

                <div className="login-card">
                    <h2>Inscription</h2>

                    <input
                        type="email"
                        placeholder="Email"
                        value={registerEmail}
                        onChange={e => setRegisterEmail(e.target.value)}
                    />

                    <input
                        type="password"
                        placeholder="Mot de passe"
                        value={registerPassword}
                        onChange={e => setRegisterPassword(e.target.value)}
                    />

                    <button className="register-button" onClick={register}>
                        Créer un compte
                    </button>
                </div>

            </div>

        </div>

    );

}


export default Auth;
