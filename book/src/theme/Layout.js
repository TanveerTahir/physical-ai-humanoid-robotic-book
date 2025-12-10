import React from 'react';
import OriginalLayout from '@theme-original/Layout';
import Footer from '@theme/Footer';

export default function Layout(props) {
  return (
    <>
      <OriginalLayout {...props}>
        {props.children}
        <Footer />
      </OriginalLayout>
    </>
  );
}