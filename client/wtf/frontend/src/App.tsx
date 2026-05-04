import './App.css'

import Chat from './components/chat/chat'
import Console from './components/console/console'
import Editor from './components/editor/editor'
import Footer from './components/footer/footer'
import Sidebar from './components/sidebar/sidebar'

function App() {
  return (
    <div className='app-container'>
      <div className='sidebar-editor-chat-console'>
        <Sidebar />
        <div className='editor-chat-console'>
          <div className='editor-chat'>
            <Editor />
            <Chat />
          </div>
          <Console />
        </div>
      </div>
      <Footer />
    </div>
  );
}

export default App;
