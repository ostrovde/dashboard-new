import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  componentDidCatch(error, info) {
    // Логируем, чтобы видеть, если случится ChunkLoadError
    console.warn('Chunk load error:', error, info);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 16 }}>
          Не удалось загрузить модуль.&nbsp;
          <button onClick={() => location.reload()}>Перезагрузить</button>
        </div>
      );
    }
    return this.props.children;
  }
}
