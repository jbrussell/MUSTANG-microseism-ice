


def plot_station_dof(station, dof, plotunit=2, lopct=10, hipct=90, closefig=True):
    hh, ax = plt.subplots()
    freq_mesh, acc_mesh = np.meshgrid(station.freqs[dof], station.acc[dof])
    pcol = ax.pcolormesh(freq_mesh, acc_mesh/(2*np.pi*freq_mesh)**(2-plotunit), station.acc_histograms[dof][:-1,:-1],
                  shading='flat', vmin=0, vmax=1.1*np.max(station.acc_histograms[dof]), cmap='viridis')
    pcol.set_edgecolor('face')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.loglog(station.freqs[dof], station.text_percentiles[dof][50]/(2*np.pi*station.freqs[dof])**(2-plotunit),
              c='k', lw=2, linestyle='-', label='{}th percentile'.format(50))
    ax.loglog(station.freqs[dof], station.text_percentiles[dof][hipct]/(2*np.pi*station.freqs[dof])**(2-plotunit),
              c='r', lw=2, linestyle='--', label='{}th percentile'.format(hipct))
    ax.loglog(station.freqs[dof], station.text_percentiles[dof][lopct]/(2*np.pi*station.freqs[dof])**(2-plotunit),
              c='r', lw=2, linestyle=':', label='{}th percentile'.format(lopct))
    ax.loglog(station.freqs[dof], accNLNM(station.freqs[dof]) / (2*np.pi*station.freqs[dof])**(2-plotunit),
              c=cList[0], label='NLNM')
    ax.loglog(station.freqs[dof], accNHNM(station.freqs[dof]) / (2*np.pi*station.freqs[dof])**(2-plotunit),
              c=cList[1], label='NHNM')
    ax.set_xlim([5e-3, 16])
    ax.set_xlabel('Frequency / Hz')
    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(
        lambda xx, _: '{:g}'.format(xx)[::-1].replace('0000', r'000,\0')[::-1]))
    thelabel = station.label + '\n' + station.network + ' ' + station.station + ' ' + station.channels[dof]
    if plotunit == 0:
        ax.set_ylim([min(accNLNM(station.freqs[dof])), max(accNHNM(station.freqs[dof]))])
        ax.set_ylabel('Displacement noise / $\bigl(\mathrm{m}\,\mathrm{Hz}^{-1/2}\bigr)$')
        ax.legend(loc='upper right')
        ax.text(0.01, 0.01, thelabel, ha='left', va='bottom', transform=ax.transAxes)
    elif plotunit == 1:
        ax.set_ylim([min(accNLNM(station.freqs[dof])), max(accNHNM(station.freqs[dof]))])
        ax.set_ylabel('Velocity noise / $\bigl(\mathrm{m}\,\mathrm{s}^{-1}\,\mathrm{Hz}^{-1/2}\bigr)$')
        ax.legend(loc='upper right')
        ax.text(0.01, 0.01, thelabel, ha='left', va='bottom', transform=ax.transAxes)
    elif plotunit == 2:
        ax.set_ylim([min(accNLNM(station.freqs[dof])), max(accNHNM(station.freqs[dof]))])
        # ax.set_ylabel(r'Acceleration noise / $\bigl(\mathrm{m}\,\mathrm{s}^{-2}\,\mathrm{Hz}^{-1/2}\bigr)$')
        ax.set_ylabel(r'Acceleration noise / $(m^2 s^{-4} Hz)$')
        ax.legend(loc='upper left',fontsize=8)
        ax.text(0.99, 0.01, thelabel, ha='right', va='bottom', transform=ax.transAxes)
    plt.show()
    figpath = './Figures/'
    if not os.path.exists(figpath):
        os.makedirs(figpath)
    hh.savefig(figpath+'{}_{}_{}'.format(station.network, station.station, station.channels[dof]) + '_dark'*dark + '.pdf')
    # if dark is True:
    #     hh.savefig(figpath+'{}_{}_{}_dark_black.pdf'.format(station.network, station.station, station.channels[dof]), facecolor='k')
    if closefig:
        plt.close(hh)