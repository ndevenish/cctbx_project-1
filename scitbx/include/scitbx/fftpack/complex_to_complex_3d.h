/* Copyright (c) 2001-2002 The Regents of the University of California
   through E.O. Lawrence Berkeley National Laboratory, subject to
   approval by the U.S. Department of Energy.
   See files COPYRIGHT.txt and LICENSE.txt for further details.

   Revision history:
     2002 Aug: Copy from cctbx/fftbx (rwgk)
     2001 Dec: iterator-based interface (rwgk)
     2001 Nov: fftbx started, based on fftpack41 (rwgk)
 */

#ifndef SCITBX_FFTPACK_COMPLEX_TO_COMPLEX_3D_H
#define SCITBX_FFTPACK_COMPLEX_TO_COMPLEX_3D_H

#include <scitbx/error.h>
#include <scitbx/array_family/tiny_reductions.h>
#include <scitbx/fftpack/complex_to_complex.h>

namespace scitbx { namespace fftpack {

  //! 3-dimensional complex-to-complex Fast Fourier Transformation.
  template <typename RealType,
            typename ComplexType = std::complex<RealType> >
  class complex_to_complex_3d
  {
    public:
#ifndef DOXYGEN_SHOULD_SKIP_THIS
      typedef RealType real_type;
      typedef ComplexType complex_type;
#endif // DOXYGEN_SHOULD_SKIP_THIS

      //! Default constructor.
      complex_to_complex_3d() {}
      //! Initialization for transforms of lengths N.
      /*! See also: Constructor of complex_to_complex.
       */
      complex_to_complex_3d(const af::int3& N);
      //! Initialization for transforms of lengths N0, N1, N2.
      /*! See also: Constructor of complex_to_complex.
       */
      complex_to_complex_3d(std::size_t N0, std::size_t N1, std::size_t N2);
      //! Access the N (or N0, N1, N2) that was passed to the constructor.
      af::int3 N() const {
        return af::int3(m_fft1d[0].N(), m_fft1d[1].N(), m_fft1d[2].N());
      }
      //! In-place "forward" Fourier transformation.
      /*! See also: complex_to_complex
       */
      template <typename MapType>
      void forward(MapType map) {
        transform(select_sign<forward_tag>(), map);
      }
      //! In-place "backward" Fourier transformation.
      /*! See also: complex_to_complex
       */
      template <typename MapType>
      void backward(MapType map) {
        transform(select_sign<backward_tag>(), map);
      }
    protected:
      // This accepts complex or real maps.
      template <typename Tag, typename MapType>
      void transform(select_sign<Tag> tag, MapType map) {
        typedef typename MapType::value_type real_or_complex_type;
        transform(tag, map, real_or_complex_type());
      }
      // Cast map of real to map of complex.
      template <typename Tag, typename MapType>
      void transform(select_sign<Tag> tag, MapType map, real_type) {
        typedef typename MapType::accessor_type accessor_type;
        accessor_type dim_real(map.accessor());
        if (dim_real[2] % 2 != 0) {
          throw error("Number of elements in third dimension must be even.");
        }
        af::ref<complex_type, accessor_type> cmap(
          reinterpret_cast<complex_type*>(map.begin()),
          accessor_type(dim_real[0], dim_real[1], dim_real[2] / 2));
        transform(tag, cmap, complex_type());
      }
      // Core routine always works on complex maps.
      template <typename Tag, typename MapType>
      void transform(select_sign<Tag> tag, MapType map, complex_type) {
  // FUTURE: move out of class body
  {
    complex_type* Seq = &(*(m_Seq.begin()));
    for (std::size_t iz = 0; iz < m_fft1d[2].N(); iz++) {
      for (std::size_t iy = 0; iy < m_fft1d[1].N(); iy++) {
        std::size_t ix;
        for (ix = 0; ix < m_fft1d[0].N(); ix++) {
          Seq[ix] = map(ix, iy, iz);
        }
        // Transform along x (slow direction)
        m_fft1d[0].transform(tag, Seq);
        for (ix = 0; ix < m_fft1d[0].N(); ix++) {
          map(ix, iy, iz) = Seq[ix];
        }
      }
      for (std::size_t ix = 0; ix < m_fft1d[0].N(); ix++) {
        std::size_t iy;
        for (iy = 0; iy < m_fft1d[1].N(); iy++) {
          Seq[iy] = map(ix, iy, iz);
        }
        // Transform along y (medium direction)
        m_fft1d[1].transform(tag, Seq);
        for (iy = 0; iy < m_fft1d[1].N(); iy++) {
          map(ix, iy, iz) = Seq[iy];
        }
      }
    }
    for (std::size_t ix = 0; ix < m_fft1d[0].N(); ix++) {
      for (std::size_t iy = 0; iy < m_fft1d[1].N(); iy++) {
        // Transform along z (fast direction)
        m_fft1d[2].transform(tag, &map(ix, iy, 0));
      }
    }
  }
      }
    private:
      af::tiny<complex_to_complex<real_type, complex_type>, 3> m_fft1d;
      af::shared<complex_type> m_Seq;
  };

  template <typename RealType, typename ComplexType>
  complex_to_complex_3d<RealType, ComplexType
    >::complex_to_complex_3d(const af::int3& N)
    : m_Seq(af::max(N))
  {
    for(std::size_t i=0;i<3;i++) {
      m_fft1d[i] = complex_to_complex<real_type, complex_type>(N[i]);
    }
  }

  template <typename RealType, typename ComplexType>
  complex_to_complex_3d<RealType, ComplexType
    >::complex_to_complex_3d(std::size_t N0, std::size_t N1, std::size_t N2)
    : m_Seq(af::max(af::tiny<std::size_t, 3>(N0, N1, N2)))
  {
    m_fft1d[0] = complex_to_complex<real_type, complex_type>(N0);
    m_fft1d[1] = complex_to_complex<real_type, complex_type>(N1);
    m_fft1d[2] = complex_to_complex<real_type, complex_type>(N2);
  }

}} // namespace scitbx::fftpack

#endif // SCITBX_FFTPACK_COMPLEX_TO_COMPLEX_3D_H
