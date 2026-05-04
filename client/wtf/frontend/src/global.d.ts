export {};

declare global {
  interface Window {
    api: {
      openFolder: () => Promise<string | null>;
    };
  }
}
